# Chen Liu, FIA

Static personal brand website for `chenliufia.com`.

## Pages

- `index.html` - Home
- `resume.html` - Professional profile
- `insights.html` - Article index
- `articles/create-and-manage-expectations.html` - First BMA reporting article
- `market-monitor.html` - Hong Kong long term insurance market monitor

## Local Preview

```bash
python3 -m http.server 8765
```

Then open:

```text
http://127.0.0.1:8765/
```

## Data Refresh

The market monitor data is generated from HKIA Excel files:

```bash
python3 scripts/process_hkia_lt.py /path/to/hkia_long_term_workbook.xlsx data/market-data.js
```

Current APE definition:

```text
APE = Annualized Premium + 10% Single Premium
```
