const data = window.HKIA_MARKET_DATA;

const colors = ["#245c73", "#47735d", "#a67830", "#8d4a46", "#337c86", "#6d6478"];

function fmtBn(value, digits = 1) {
  return Number(value).toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function fmtPct(value, digits = 1) {
  return `${(Number(value) * 100).toFixed(digits)}%`;
}

function byId(id) {
  return document.getElementById(id);
}

function renderKpis() {
  const market = data.market;
  const top = data.topInsurers[0];
  const items = [
    {
      label: "Individual NB APE",
      value: `HKD ${fmtBn(market.ape)}bn`,
      hint: "APE = annualized premium + 10% single premium",
    },
    {
      label: "Recurring premium share",
      value: fmtPct(market.recurringShare),
      hint: "Annualized premium as a share of APE",
    },
    {
      label: "Participating business share",
      value: fmtPct(market.participatingApe / market.ape),
      hint: "Dominant product class by APE",
    },
    {
      label: "Largest player",
      value: top.insurer,
      hint: `${fmtPct(top.marketShare)} market share by APE`,
    },
  ];

  byId("kpiGrid").innerHTML = items
    .map(
      (item) => `
        <article class="kpi">
          <p class="label">${item.label}</p>
          <p class="value">${item.value}</p>
          <p class="hint">${item.hint}</p>
        </article>
      `
    )
    .join("");
}

function stackRows(items, options = {}) {
  const max = options.max || Math.max(...items.map((item) => item.ape || item.value || 0));
  return items
    .map((item, index) => {
      const value = item.ape ?? item.value;
      const share = item.share ?? value / max;
      const width = Math.max(1, share * 100);
      return `
        <div class="stack-row">
          <div class="row-top">
            <strong>${item.name}</strong>
            <span>${fmtPct(share)} | HKD ${fmtBn(value)}bn</span>
          </div>
          <div class="track"><div class="fill" style="width:${width}%; background:${colors[index % colors.length]}"></div></div>
        </div>
      `;
    })
    .join("");
}

function barRows(items, options = {}) {
  const max = options.max || Math.max(...items.map((item) => item.ape || 0));
  return items
    .map((item, index) => {
      const value = item.ape;
      const shareText = item.marketShare ? `${fmtPct(item.marketShare)} share` : `SP ${fmtBn(item.sp)}bn | AP ${fmtBn(item.ap)}bn`;
      const recurring = item.recurringShare ? `<div class="bar-meta">${fmtPct(item.recurringShare)} recurring share</div>` : "";
      return `
        <div class="bar-item">
          <div class="bar-label">
            ${item.insurer || item.name}
            <div class="bar-meta">${shareText}</div>
            ${recurring}
          </div>
          <div class="track">
            <div class="fill" style="width:${Math.max(1, (value / max) * 100)}%; background:${colors[index % colors.length]}"></div>
          </div>
          <div class="bar-value">${fmtBn(value)}bn</div>
        </div>
      `;
    })
    .join("");
}

function renderMixes() {
  byId("productClassMix").innerHTML = stackRows(data.productClassMix);
  byId("channelMix").innerHTML = stackRows(data.channelMix);
  byId("currencyMix").innerHTML = stackRows(data.currencyMix);
  byId("productBars").innerHTML = barRows(data.topProducts.slice(0, 7));
  byId("insurerBars").innerHTML = barRows(data.topInsurers);
}

function renderBehaviour() {
  const b = data.inforceLapse;
  const cards = [
    ["In-force policies", `${fmtBn(b.policiesM, 2)}m`, "Policies at period end"],
    ["Renewal premiums", `HKD ${fmtBn(b.renewalPremiumReceivable)}bn`, "Premiums receivable"],
    ["Claims and benefits", `HKD ${fmtBn(b.totalClaimsBenefits)}bn`, "Paid during the period"],
    ["Early surrender share", fmtPct(b.earlySurrenderShare), "Of total surrender benefits"],
  ];

  byId("behaviourGrid").innerHTML = cards
    .map(
      ([label, value, hint]) => `
        <article class="mini-card">
          <p class="label">${label}</p>
          <p class="value">${value}</p>
          <p class="hint">${hint}</p>
        </article>
      `
    )
    .join("");
}

function renderTable() {
  byId("appendixRows").innerHTML = data.topInsurers
    .map(
      (item, index) => `
        <tr>
          <td>${index + 1}</td>
          <td>${item.insurer}</td>
          <td>${fmtBn(item.ape)}</td>
          <td>${fmtPct(item.marketShare)}</td>
          <td>${fmtBn(item.totalAp)}</td>
          <td>${fmtBn(item.totalSp)}</td>
          <td>${fmtPct(item.recurringShare)}</td>
        </tr>
      `
    )
    .join("");
}

function boot() {
  byId("periodLabel").textContent = data.period.replace("二零二五年一月至十二月 ", "");
  byId("sourceLink").href = data.sourceUrl;
  renderKpis();
  renderMixes();
  renderBehaviour();
  renderTable();
}

boot();
