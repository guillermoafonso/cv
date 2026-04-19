"""
Fetch Ipsos UK 'Political Monitor - Satisfaction Ratings 1997-Present'
and produce a tidy CSV of net PM satisfaction for the 8 most recent PMs.

Run:
    pip install -r ../requirements.txt
    python fetch_ipsos.py

Outputs:
    ../data/raw/ipsos_<timestamp>.html       raw page (provenance)
    ../data/raw/<chart-provider>_*.json|csv  raw chart payloads if found
    ../data/pm_satisfaction.csv              tidy data (if parse succeeded)
    ../data/PARSE_FAILED.txt                 diagnostic bundle (if not)

Design: Ipsos renders its trend chart with an interactive embed (historically
Flourish, sometimes Datawrapper or custom). Rather than hardcode a brittle
selector, we save the raw page, probe for known embed providers, fetch their
public data URLs, and attempt to normalise. If nothing matches, we leave a
detailed diagnostic so the parsing step can be adjusted with eyes on the HTML.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
from bs4 import BeautifulSoup

IPSOS_URL = "https://www.ipsos.com/en-uk/political-monitor-satisfaction-ratings-1997-present"

# Browser-like headers; Ipsos 403s on the default requests UA.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}


# The 8 PMs we care about, with accession dates. Dates are well-established.
@dataclass(frozen=True)
class PM:
    key: str          # short key used in the CSV
    label: str        # label used on the plot (matches your example)
    start: date       # first day in office


PMS: list[PM] = [
    PM("blair",   "Blair (1997)",    date(1997, 5, 2)),
    PM("brown",   "Brown (2007)",    date(2007, 6, 27)),
    PM("cameron", "Cameron (2010)",  date(2010, 5, 11)),
    PM("may",     "May (2016)",      date(2016, 7, 13)),
    PM("johnson", "Johnson (2019)",  date(2019, 7, 24)),
    PM("truss",   "Truss (2022)",    date(2022, 9, 6)),
    PM("sunak",   "Sunak (2022)",    date(2022, 10, 25)),
    PM("starmer", "Starmer (2024)",  date(2024, 7, 5)),
]

# Surname -> PM, used to map whatever label the chart uses onto our canonical set.
PM_BY_SURNAME = {p.key: p for p in PMS}


def log(msg: str) -> None:
    print(f"[fetch_ipsos] {msg}", file=sys.stderr)


def get(url: str, session: requests.Session) -> requests.Response:
    log(f"GET {url}")
    r = session.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r


def find_embeds(html: str) -> list[dict]:
    """Return a list of chart-embed descriptors found in the page."""
    soup = BeautifulSoup(html, "lxml")
    embeds: list[dict] = []

    for iframe in soup.find_all("iframe"):
        src = (iframe.get("src") or "").strip()
        if not src:
            continue
        if "flourish.studio" in src:
            m = re.search(r"visualisation/(\d+)", src)
            if m:
                embeds.append({"provider": "flourish", "id": m.group(1), "src": src})
        elif "datawrapper" in src or "dwcdn.net" in src:
            m = re.search(r"/([A-Za-z0-9]{4,6})/?", src)
            if m:
                embeds.append({"provider": "datawrapper", "id": m.group(1), "src": src})

    # Custom Highcharts-style payloads sometimes embedded as JSON in <script>
    for script in soup.find_all("script"):
        text = script.string or ""
        if "series" in text and ("satisfaction" in text.lower() or "prime minister" in text.lower()):
            embeds.append({"provider": "inline-script", "src": None, "text": text[:2000]})

    return embeds


def fetch_flourish(viz_id: str, session: requests.Session, raw_dir: Path) -> dict | None:
    """Flourish exposes the chart data at a predictable URL."""
    url = f"https://public.flourish.studio/visualisation/{viz_id}/visualisation.json"
    try:
        r = get(url, session)
    except Exception as e:  # noqa: BLE001 - we want to log anything and continue
        log(f"flourish fetch failed: {e}")
        return None
    payload = r.json()
    (raw_dir / f"flourish_{viz_id}.json").write_text(json.dumps(payload, indent=2))
    return payload


def fetch_datawrapper(chart_id: str, session: requests.Session, raw_dir: Path) -> str | None:
    url = f"https://datawrapper.dwcdn.net/{chart_id}/dataset.csv"
    try:
        r = get(url, session)
    except Exception as e:  # noqa: BLE001
        log(f"datawrapper fetch failed: {e}")
        return None
    (raw_dir / f"datawrapper_{chart_id}.csv").write_text(r.text)
    return r.text


def parse_flourish(payload: dict) -> pd.DataFrame | None:
    """
    Try to flatten a Flourish 'line chart' payload into (series, x, y).

    Flourish payloads vary. The common shape we look for is:
      payload["data"]["data"] is a list of row dicts with a label column and
      one column per politician. We try a few permutations before giving up.
    """
    try:
        rows = payload["data"]["data"]
    except (KeyError, TypeError):
        return None
    if not isinstance(rows, list) or not rows:
        return None
    df = pd.DataFrame(rows)
    # First column is usually a date-ish label.
    if df.shape[1] < 2:
        return None
    date_col = df.columns[0]
    melted = df.melt(id_vars=[date_col], var_name="series", value_name="net").dropna()
    melted = melted.rename(columns={date_col: "fieldwork_date_raw"})
    return melted


def normalise(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise the melted long-format frame into our output schema:
    pm, fieldwork_date, net_satisfaction, months_in_office, source.
    """
    out_rows: list[dict] = []
    for _, row in df.iterrows():
        series = str(row["series"]).strip().lower()
        pm_key = next((k for k in PM_BY_SURNAME if k in series), None)
        if pm_key is None:
            continue
        pm = PM_BY_SURNAME[pm_key]
        raw = str(row["fieldwork_date_raw"])
        fw = parse_date(raw)
        if fw is None or fw < pm.start:
            continue
        try:
            net = float(row["net"])
        except (TypeError, ValueError):
            continue
        months = (fw - pm.start).days / 30.4375
        out_rows.append(
            {
                "pm": pm.key,
                "label": pm.label,
                "fieldwork_date": fw.isoformat(),
                "net_satisfaction": net,
                "months_in_office": round(months, 2),
            }
        )
    return pd.DataFrame(out_rows).sort_values(["pm", "fieldwork_date"])


def parse_date(s: str) -> date | None:
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d %b %Y", "%b %Y", "%B %Y", "%Y-%m"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    # Year-only ("1997") - too coarse; skip.
    return None


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data",
        help="Output data directory (default: ../data)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    data_dir: Path = args.out
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # 1. Save the canonical Ipsos page for provenance.
    try:
        page = get(IPSOS_URL, session)
    except Exception as e:  # noqa: BLE001
        log(f"FATAL: could not fetch Ipsos page: {e}")
        return 2
    raw_html = raw_dir / f"ipsos_{stamp}.html"
    raw_html.write_text(page.text)
    log(f"saved raw page: {raw_html} ({len(page.text):,} bytes)")

    # 2. Probe for chart embeds.
    embeds = find_embeds(page.text)
    log(f"found {len(embeds)} embed candidate(s): {[e['provider'] for e in embeds]}")

    # 3. Try to pull data from each in turn.
    tidy: pd.DataFrame | None = None
    for e in embeds:
        if e["provider"] == "flourish":
            payload = fetch_flourish(e["id"], session, raw_dir)
            if payload is None:
                continue
            melted = parse_flourish(payload)
            if melted is None or melted.empty:
                continue
            tidy = normalise(melted)
            if not tidy.empty:
                log(f"parsed {len(tidy)} rows from flourish id={e['id']}")
                break
        elif e["provider"] == "datawrapper":
            csv_text = fetch_datawrapper(e["id"], session, raw_dir)
            if not csv_text:
                continue
            try:
                wide = pd.read_csv(pd.io.common.StringIO(csv_text))
            except Exception as ex:  # noqa: BLE001
                log(f"datawrapper parse failed: {ex}")
                continue
            date_col = wide.columns[0]
            melted = wide.melt(id_vars=[date_col], var_name="series", value_name="net").dropna()
            melted = melted.rename(columns={date_col: "fieldwork_date_raw"})
            tidy = normalise(melted)
            if not tidy.empty:
                log(f"parsed {len(tidy)} rows from datawrapper id={e['id']}")
                break

    if tidy is None or tidy.empty:
        diag = data_dir / "PARSE_FAILED.txt"
        diag.write_text(
            "Could not auto-parse the Ipsos chart.\n\n"
            f"Saved raw HTML: {raw_html}\n"
            f"Embed candidates: {json.dumps(embeds, indent=2)}\n\n"
            "Next step: open the raw HTML, identify the chart source, and "
            "extend fetch_ipsos.py with a matching handler.\n"
        )
        log(f"WROTE {diag} — auto-parse failed. See file for next steps.")
        return 1

    # 4. Persist.
    out_csv = data_dir / "pm_satisfaction.csv"
    tidy.insert(0, "source", IPSOS_URL)
    tidy.to_csv(out_csv, index=False)
    log(f"wrote {out_csv} ({len(tidy):,} rows, {tidy['pm'].nunique()} PMs)")

    # Quick coverage summary so the user can eyeball gaps.
    summary = tidy.groupby("pm").agg(
        n_polls=("net_satisfaction", "size"),
        first=("fieldwork_date", "min"),
        last=("fieldwork_date", "max"),
    )
    log("coverage:\n" + summary.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
