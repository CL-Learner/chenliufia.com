# HKIA Long Term Insurance Market Monitor

## Positioning

This page is not intended to be a plain visualization of IA statistics. Its purpose is to show public market data interpreted through an actuarial and market lens.

Working title:

Hong Kong Long Term Insurance Market Monitor

Core promise:

IA provisional statistics, interpreted through an actuarial and market lens.

## Page Structure

1. Hero
   - Brand signal: Chen Liu, FIA
   - Monitor title
   - Period and IA source link

2. Chen's Take
   - 3 concise market interpretations
   - Current first edition themes:
     - APE is useful, but incomplete
     - Participating business remains the centre of gravity
     - Mainland visitor data needs a footnote

3. Market Pulse
   - Individual new business APE
   - Recurring premium share
   - Participating business share
   - Largest player by APE

4. NB Overview
   - Product class mix
   - Distribution channel mix
   - Product line ranking
   - Currency mix

5. Key Players
   - Top insurers by APE
   - Market share
   - Recurring premium share

6. In-force And Behaviour
   - In-force policies
   - Renewal premiums
   - Claims and benefits
   - Early surrender benefits as a share of surrender benefits

7. Appendix
   - Top player table
   - APE formula and source notes

## Interpretation Principles

- Use fewer charts, but attach a clear market interpretation to each module.
- Treat APE ranking as a starting point, not a conclusion.
- Always distinguish headline growth from growth quality.
- Read product mix together with bonus governance, policyholder expectations, and long-term cash flow.
- Read channel mix as a proxy for customer segment, sales economics, and sustainability.
- Treat Mainland visitor statistics carefully because IA paused separate 2025 publication during its review of non-local policyholder data collection.

## Data Pipeline

Source workbook:

`/Users/chenl_macbook/Downloads/4q25long.xlsx`

Generated data file:

`data/market-data.js`

Processing script:

`scripts/process_hkia_lt.py`

Current APE definition:

`APE = Annualized Premium + 10% Single Premium`

To refresh with a new IA workbook:

```bash
/Users/chenl_macbook/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/process_hkia_lt.py /path/to/new_workbook.xlsx data/market-data.js
```

## Future Enhancements

- Add historical trend once 2024 and earlier comparable files are processed.
- Add rank movement after a second period is loaded.
- Add a Mainland Business archive through 2024, with a clear methodology note for the 2025 disclosure gap.
- Add individual insurer profile panels for the top 5 players.
- Convert this prototype into an Astro or Next.js page when the main personal website is built.
