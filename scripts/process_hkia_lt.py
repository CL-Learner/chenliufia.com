from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import pandas as pd


SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/chenl_macbook/Downloads/4q25long.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[1] / "data" / "market-data.js"


def clean_name(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def num(value):
    if pd.isna(value) or value == "":
        return 0.0
    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0.0
    if math.isnan(value):
        return 0.0
    return value


def hkdbn(value):
    return num(value) / 1_000_000


def ape(sp, ap):
    return num(ap) + 0.1 * num(sp)


def english_label(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if "\n" in text:
        return clean_name(text.split("\n")[-1])
    return clean_name(text)


def extract_period(workbook_path):
    raw = pd.read_excel(workbook_path, sheet_name="Form LT QR (NB)", header=None)
    value = clean_name(raw.iloc[1, 2])
    if "\n" in value:
        return value.split("\n")[-1].strip()
    return value


def table_l1(workbook_path):
    df = pd.read_excel(workbook_path, sheet_name="Table L1", header=None)
    data = df.iloc[8:].copy()
    data = data[data[0].notna()]
    records = []
    market_total = None
    for _, row in data.iterrows():
        name = clean_name(row[0])
        rec = {
            "insurer": name,
            "insurerZh": clean_name(row[1]),
            "participatingSp": hkdbn(row[2]),
            "participatingAp": hkdbn(row[3]),
            "otherSp": hkdbn(row[4]),
            "otherAp": hkdbn(row[5]),
            "linkedSp": hkdbn(row[6]),
            "linkedAp": hkdbn(row[7]),
            "totalSp": hkdbn(row[8]),
            "totalAp": hkdbn(row[9]),
            "ape": hkdbn(ape(row[8], row[9])),
        }
        rec["recurringShare"] = rec["totalAp"] / rec["ape"] if rec["ape"] else 0
        rec["singlePremiumShare"] = (0.1 * rec["totalSp"]) / rec["ape"] if rec["ape"] else 0
        rec["participatingApe"] = hkdbn(ape(row[2], row[3]))
        rec["otherApe"] = hkdbn(ape(row[4], row[5]))
        rec["linkedApe"] = hkdbn(ape(row[6], row[7]))
        if name == "Market Total":
            market_total = rec
        else:
            records.append(rec)
    records = [r for r in records if r["ape"] > 0]
    records.sort(key=lambda r: r["ape"], reverse=True)
    if market_total:
        for record in records:
            record["marketShare"] = record["ape"] / market_total["ape"]
    return records, market_total


def form_mix(workbook_path, sheet, labels, sp_ap_cols):
    df = pd.read_excel(workbook_path, sheet_name=sheet, header=None)
    total = df[df[1].astype(str).str.contains("總額\\nTotal", na=False)]
    if total.empty:
        total = df[df[0].astype(str).str.contains("Market Total", na=False)]
    row = total.iloc[-1]
    output = []
    for label, (sp_col, ap_col) in zip(labels, sp_ap_cols):
        sp = hkdbn(row[sp_col])
        ap = hkdbn(row[ap_col])
        output.append({"name": label, "sp": sp, "ap": ap, "ape": hkdbn(ape(row[sp_col], row[ap_col]))})
    total_ape = sum(item["ape"] for item in output)
    for item in output:
        item["share"] = item["ape"] / total_ape if total_ape else 0
    return output


def product_rows(workbook_path):
    df = pd.read_excel(workbook_path, sheet_name="Form LT QR (NB)", header=None)
    rows = []
    group = ""
    for _, row in df.iloc[7:39].iterrows():
        label = english_label(row[1])
        if not label:
            continue
        if label in {"Participating Business", "Other Businesses", "Linked Long Term (Class C)"}:
            group = {
                "Participating Business": "Par",
                "Other Businesses": "Other",
                "Linked Long Term (Class C)": "Linked",
            }[label]
            continue
        if label.startswith("Total") or "Total of" in label:
            continue
        sp = hkdbn(row[7])
        ap = hkdbn(row[8])
        value = hkdbn(ape(row[7], row[8]))
        if value <= 0:
            continue
        name = f"{group} - {label}" if group else label
        rows.append({"name": name, "sp": sp, "ap": ap, "ape": value})
    rows.sort(key=lambda item: item["ape"], reverse=True)
    return rows


def inforce_lapse(workbook_path):
    inf = pd.read_excel(workbook_path, sheet_name="Form LT QR (IF)", header=None)
    inf_total = inf[inf[1].astype(str).str.contains("總額\\nTotal", na=False)].iloc[-1]
    lapse = pd.read_excel(workbook_path, sheet_name="Form LT QR (Lapse)", header=None)
    lapse_total = lapse[lapse[1].astype(str).str.contains("總額\\nTotal", na=False)].iloc[-1]
    total_claims_benefits = sum(hkdbn(lapse_total[col]) for col in range(10, 18))
    early_surrender = hkdbn(lapse_total[10]) + hkdbn(lapse_total[11])
    total_surrender = hkdbn(lapse_total[13])
    return {
        "policiesM": num(inf_total[2]) / 1_000_000,
        "singlePremiumReceivable": hkdbn(inf_total[5]),
        "firstYearPremiumReceivable": hkdbn(inf_total[6]),
        "renewalPremiumReceivable": hkdbn(inf_total[7]),
        "totalClaimsBenefits": total_claims_benefits,
        "totalSurrenderBenefits": total_surrender,
        "earlySurrenderBenefits": early_surrender,
        "earlySurrenderShare": early_surrender / total_surrender if total_surrender else 0,
    }


def channel_for_insurer(workbook_path, top_names):
    df = pd.read_excel(workbook_path, sheet_name="Table L1 (channel)", header=None)
    rows = df.iloc[9:].copy()
    channels = [
        ("Agency", 14, 15),
        ("Bancassurance", 16, 17),
        ("Broker", 18, 19),
        ("Direct", 20, 21),
        ("Others", 22, 23),
    ]
    output = {}
    for _, row in rows.iterrows():
        name = clean_name(row[0])
        if name not in top_names:
            continue
        parts = []
        total = 0
        for label, sp_col, ap_col in channels:
            value = hkdbn(ape(row[sp_col], row[ap_col]))
            parts.append({"name": label, "ape": value})
            total += value
        for part in parts:
            part["share"] = part["ape"] / total if total else 0
        output[name] = parts
    return output


def main():
    records, market = table_l1(SOURCE)
    top10 = records[:10]
    channel_mix = form_mix(
        SOURCE,
        "Form LT QR (channel)",
        ["Agency", "Bancassurance", "Broker", "Direct", "Others"],
        [(14, 15), (16, 17), (18, 19), (20, 21), (22, 23)],
    )
    currency_mix = form_mix(
        SOURCE,
        "Form LT QR (CCY)",
        ["HKD", "RMB", "USD", "Other"],
        [(12, 13), (14, 15), (16, 17), (18, 19)],
    )
    premium_term_mix = form_mix(
        SOURCE,
        "Form LT QR (prem term)",
        ["Single", "<5 years", "5-10 years", "10-25 years", "25+ years"],
        [(8, 8), (9, 9), (10, 10), (11, 11), (12, 12)],
    )
    payload = {
        "sourceFile": SOURCE.name,
        "sourceUrl": "https://www.ia.org.hk/en/infocenter/statistics/market_7_2025.html",
        "period": extract_period(SOURCE),
        "unit": "HKD billion unless otherwise stated",
        "market": market,
        "topInsurers": top10,
        "allInsurers": records,
        "productClassMix": [
            {"name": "Participating", "ape": market["participatingApe"], "share": market["participatingApe"] / market["ape"]},
            {"name": "Other non-linked", "ape": market["otherApe"], "share": market["otherApe"] / market["ape"]},
            {"name": "Linked", "ape": market["linkedApe"], "share": market["linkedApe"] / market["ape"]},
        ],
        "topProducts": product_rows(SOURCE)[:8],
        "channelMix": channel_mix,
        "currencyMix": currency_mix,
        "premiumTermMix": premium_term_mix,
        "topInsurerChannels": channel_for_insurer(SOURCE, {item["insurer"] for item in top10[:6]}),
        "inforceLapse": inforce_lapse(SOURCE),
        "notes": [
            "APE is calculated as annualized premium plus 10% of single premium.",
            "Figures are based on HKIA provisional long term business statistics and are unaudited.",
            "Separate Mainland visitor statistics are not available for 2025 pending IA's review of non-local policyholder data collection scope and criteria.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("window.HKIA_MARKET_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
