# The Last Mile of Political Money

An interactive data investigation that traces FEC disbursement data to show where political money actually lands at the street level. I made this partly for fun, but also partly because I could not find a story that covered this data in this way. 

Everyone knows where campaign money comes from. This project maps what it actually buys — which vendors, in which cities, for which services — using 4.8 million expenditure records across the 2020, 2022, and 2024 election cycles.

**[View the project &rarr;](#)** (update with your deployed URL)

## What this shows

- **154,000+ political vendors** mapped by location, sized by dollars received, colored by party
- **Street-level clustering** revealing how political spending concentrates in a handful of firms
- **Spending purpose breakdowns** — media buying, consulting, direct mail, polling, and more
- **Committee and candidate linkage** — which candidates' money flows to which vendors
- **Multi-cycle analysis** — the same vendors appear election after election

## How it works

### Data pipeline (Python)

The `pipeline/` directory contains a reproducible Python pipeline that:

1. Downloads FEC bulk data files for 2020, 2022, and 2024
2. Parses pipe-delimited flat files and merges with committee/candidate master files
3. Deduplicates ~290,000 vendor name variants using fuzzy string matching (rapidfuzz)
4. Geocodes vendor locations via ZIP code centroids
5. Categorizes free-text spending purposes into standardized categories
6. Exports GeoJSON and JSON for the frontend

### Frontend (SvelteKit)

The `web/` directory is a SvelteKit app with:

- **Scrollytelling narrative** — a guided story with D3 choropleth, MapLibre vendor map, treemap, and cycle timeline
- **Interactive explorer** — search, filter by party/state/spend, click vendors for detailed profiles with spending timelines, purpose breakdowns, and committee lists
- **Data table view** — sortable, paginated table of all vendors
- **Static deployment** — builds to a self-contained static site via `@sveltejs/adapter-static`

## Run it yourself

### Frontend

```bash
cd web
npm install
npm run dev
```

### Data pipeline

```bash
cd pipeline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pipeline.src.run_pipeline
```

This downloads ~200MB of FEC data and processes ~4.8M records. Takes about 5-10 minutes.

## Tech stack

| Layer | Tools |
|-------|-------|
| Data pipeline | Python, pandas, rapidfuzz, httpx, pyarrow |
| Frontend | SvelteKit 2, Svelte 5, TypeScript |
| Visualization | D3.js v7, MapLibre GL JS v5 |
| Map tiles | CARTO Positron |
| Deployment | Static site (GitHub Pages / Netlify / Vercel) |

## Data sources

- [FEC Bulk Data](https://www.fec.gov/data/browse-data/?tab=bulk-data) — operating expenditures, committee master, candidate master
- [US Atlas TopoJSON](https://github.com/topojson/us-atlas) — state boundaries
- ZIP code centroids — U.S. Census derived

## Contact

For data requests or questions: **lysiktory@gmail.com**

## License

Data is public (FEC). Code is open source.
