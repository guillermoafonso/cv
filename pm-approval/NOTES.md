# PM satisfaction trajectories

Reproduces the example chart (net satisfaction vs. months in office) for the 8 most recent UK Prime Ministers using a single, consistent Ipsos series.

## What I'm measuring

**Ipsos UK Political Monitor — "Satisfaction with the Prime Minister."** The question wording has been stable since 1977: *"Are you satisfied or dissatisfied with the way [X] is doing their job as Prime Minister?"* The metric plotted is **net satisfaction = % satisfied − % dissatisfied**.

This is the only long-running, consistent UK PM-approval series — so using just Ipsos gives cleaner cross-PM comparisons than mixing in YouGov, Opinium, etc. The tradeoff: fewer data points (Ipsos polls roughly monthly).

Source page: <https://www.ipsos.com/en-uk/political-monitor-satisfaction-ratings-1997-present>

## PMs and accession dates

| PM | Start | Notes |
|---|---|---|
| Blair | 1997-05-02 | |
| Brown | 2007-06-27 | |
| Cameron | 2010-05-11 | |
| May | 2016-07-13 | |
| Johnson | 2019-07-24 | |
| Truss | 2022-09-06 | 49 days in office — expect ≤2 Ipsos polls |
| Sunak | 2022-10-25 | |
| Starmer | 2024-07-05 | |

## How it works

```
pm-approval/
├── scripts/
│   ├── fetch_ipsos.py          downloads + parses the Ipsos chart data
│   └── plot_pm_satisfaction.py draws the graph from the CSV
├── data/
│   ├── raw/                    raw HTML + chart JSON (provenance)
│   └── pm_satisfaction.csv     tidy output
├── out/                        generated plots
├── requirements.txt
└── NOTES.md                    you are here
```

### Run it

```bash
cd pm-approval
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/fetch_ipsos.py
python scripts/plot_pm_satisfaction.py
```

### What the fetcher does

1. Downloads the Ipsos page with a browser User-Agent (the default `requests` UA gets 403'd).
2. Saves the raw HTML under `data/raw/ipsos_<UTC timestamp>.html` for provenance.
3. Looks for the chart embed. Ipsos currently renders this trend chart as an interactive embed (historically Flourish; sometimes Datawrapper). The script tries both — it finds the embed ID, hits the provider's public data URL, and saves the raw JSON/CSV alongside the HTML.
4. Melts the wide table (date × one column per PM) into long format, maps column names onto our PM list by surname, and writes `data/pm_satisfaction.csv`.
5. Prints a coverage summary (polls per PM, first/last fieldwork date) so gaps are obvious.

## Decisions and caveats

- **Metric choice.** Net satisfaction, not approve/disapprove. Ipsos doesn't use the word "approve" — the y-axis label in the plot reflects that.
- **Months in office** is computed as `(fieldwork_date − start_date).days / 30.4375`. The example plot appears to round to whole months; the CSV keeps the fractional value and the plot uses it as-is.
- **Truss** will likely have 1 Ipsos poll at best. The line will look like a single data point or a very short segment — that's real, not a bug.
- **Sunak / Truss overlap** — Truss's start (2022-09-06) and Sunak's start (2022-10-25) are ~7 weeks apart. Any Ipsos fieldwork in October 2022 is assigned to whichever PM held office on the fieldwork date.
- **Ipsos methodology change.** Ipsos moved from face-to-face to phone/online during 2020–2021. Net scores before vs. after the switch are broadly comparable but not identical; nothing in this script corrects for that.
- **If auto-parse fails** the fetcher writes `data/PARSE_FAILED.txt` with a diagnostic bundle. The raw HTML is still saved, so the chart-embed handler can be extended without re-downloading.

## What to check once it's run

- Row count per PM in the coverage summary. Blair should have the most (~8–10 years × ~monthly); Truss the fewest.
- First fieldwork date per PM should be after their start date.
- Net satisfaction values are bounded ≈ [−90, +70] in practice — anything outside that range suggests a parse error.
