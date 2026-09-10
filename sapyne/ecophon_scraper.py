"""Scrape an Ecophon product page and append absorption data to ecophon.csv.

Usage (command line)
--------------------
    python ecophon_scraper.py --url URL --name "Ecophon Focus A" [--csv PATH]

Usage (notebook / interactive)
-------------------------------
    from sapyne.ecophon_scraper import scrape_and_append
    scrape_and_append(
        url="https://www.ecophon.com/cz/produkty/ecophon-focus/ecophon-focus-a/",
        product_line="Ecophon Focus A",
    )

The script uses Playwright (headless Chromium) to render the JavaScript-heavy
Ecophon product pages and then parses every absorption table it finds.

Naming convention
-----------------
Each row is named:
    "<product_line> [<variant>] tl. <tl> mm o.d.s. <ods> mm"

where <variant> is the first column of the table row (may be empty).

ID format: ECPnnn  (zero-padded to 3 digits, continuing from the last
existing ID in the target CSV).
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from bs4 import BeautifulSoup

DEFAULT_CSV = Path(__file__).parent / "library" / "ecophon.csv"
FREQ_COLS = ["125", "250", "500", "1000", "2000", "4000"]


# ---------------------------------------------------------------------------
# HTML / table parsing
# ---------------------------------------------------------------------------

def _is_absorption_table(table_soup) -> bool:
    """Return True when the table looks like an absorption coefficient table."""
    text = table_soup.get_text(" ")
    return "125" in text and "250" in text and "500" in text and "1000" in text


def _cell_text(td) -> str:
    return td.get_text(" ", strip=True).rstrip(",").strip()


def _build_name(product_line: str, variant: str, tl: str, ods: str) -> str:
    name_parts = [product_line]
    if variant:
        name_parts.append(variant)
    name_parts.append(f"tl. {tl} mm o.d.s. {ods} mm")
    return " ".join(name_parts)


def _extract_balanced_object(text: str, object_start: int) -> str | None:
    """Extract a balanced {...} object starting at *object_start*."""
    if object_start < 0 or object_start >= len(text) or text[object_start] != "{":
        return None

    depth = 0
    in_str = False
    escaped = False
    for idx in range(object_start, len(text)):
        ch = text[idx]
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[object_start : idx + 1]
    return None


def _parse_embedded_acoustic_tables(html: str, product_line: str) -> list[dict]:
    """Parse Ecophon JS-embedded acoustic table data from rendered HTML."""
    key = '"acousticTables":'
    idx = html.find(key)
    if idx == -1:
        return []

    obj_start = html.find("{", idx + len(key))
    payload = _extract_balanced_object(html, obj_start)
    if not payload:
        return []

    try:
        acoustic_tables = json.loads(payload)
    except json.JSONDecodeError:
        return []

    rows_out: list[dict] = []
    for table in acoustic_tables.get("tables", []):
        if table.get("type") != "FrequencyTable":
            continue

        flat_keys: list[str] = []
        for header in table.get("headers", []):
            key_name = header.get("key", "")
            if key_name == "PracticalAbsorptionCoefficient":
                for sub in header.get("subheaders", []):
                    flat_keys.append(sub.get("key", ""))
            else:
                flat_keys.append(key_name)

        for row in table.get("rows", []):
            if not isinstance(row, list) or len(row) != len(flat_keys):
                continue

            row_map = dict(zip(flat_keys, row))
            tl = str(row_map.get("THKmm", "")).strip()
            ods = str(row_map.get("ODSmm", "")).strip()
            if not tl or not ods:
                continue

            variant = str(row_map.get("extraInfo", "")).strip().rstrip(",")
            if variant == "-":
                variant = ""

            freqs = {
                "125": str(row_map.get("Frequency125", "")).strip(),
                "250": str(row_map.get("Frequency250", "")).strip(),
                "500": str(row_map.get("Frequency500", "")).strip(),
                "1000": str(row_map.get("Frequency1000", "")).strip(),
                "2000": str(row_map.get("Frequency2000", "")).strip(),
                "4000": str(row_map.get("Frequency4000", "")).strip(),
            }
            if any(v == "" for v in freqs.values()):
                continue

            rows_out.append({"name": _build_name(product_line, variant, tl, ods), **freqs})

    return rows_out


def parse_absorption_tables(html: str, product_line: str) -> list[dict]:
    """Extract all absorption rows from rendered HTML.

    Returns a list of dicts with keys: variant, tl, ods, 125..4000.
    """
    soup = BeautifulSoup(html, "html.parser")
    rows_out: list[dict] = []

    for table in soup.find_all("table", class_="table"):
        if not _is_absorption_table(table):
            continue

        # Locate header row that has the frequency columns
        header_indices: dict[str, int] = {}
        for tr in table.find_all("tr"):
            cells = tr.find_all(["th", "td"])
            texts = [_cell_text(c) for c in cells]
            if "125 Hz" in texts or "125Hz" in texts or any("125" in t for t in texts):
                for idx, t in enumerate(texts):
                    for freq in ["125", "250", "500", "1000", "2000", "4000"]:
                        if t.startswith(freq):
                            header_indices[freq] = idx
                break

        if len(header_indices) < 6:
            continue  # not the right table

        # Infer column positions for tl, o.d.s from the second header row
        # (they are always columns 1 and 2 in Ecophon tables)
        tl_idx, ods_idx, variant_idx = 1, 2, 0

        tbody = table.find("tbody")
        if not tbody:
            continue

        for tr in tbody.find_all("tr"):
            cells = tr.find_all("td")
            if not cells:
                continue
            try:
                variant = _cell_text(cells[variant_idx]) if len(cells) > variant_idx else ""
                tl = _cell_text(cells[tl_idx]) if len(cells) > tl_idx else ""
                ods = _cell_text(cells[ods_idx]) if len(cells) > ods_idx else ""
                freqs = {
                    freq: _cell_text(cells[header_indices[freq]])
                    for freq in FREQ_COLS
                    if freq in header_indices and len(cells) > header_indices[freq]
                }
            except (IndexError, KeyError):
                continue

            if not tl.lstrip("-").isdigit() and not re.match(r"^\d", tl):
                continue  # skip header-like data rows

            if len(freqs) < 6:
                continue

            rows_out.append({"name": _build_name(product_line, variant, tl, ods), **freqs})

    # New Ecophon pages often expose the acoustic data in embedded JSON.
    rows_out.extend(_parse_embedded_acoustic_tables(html, product_line))

    # Keep insertion order while removing exact duplicates.
    seen: set[tuple[str, str, str, str, str, str, str]] = set()
    deduped_rows: list[dict] = []
    for row in rows_out:
        key = (
            row["name"],
            row["125"],
            row["250"],
            row["500"],
            row["1000"],
            row["2000"],
            row["4000"],
        )
        if key in seen:
            continue
        seen.add(key)
        deduped_rows.append(row)

    return deduped_rows


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def _last_id(csv_path: Path) -> int:
    """Return the numeric part of the last ECP ID in the CSV."""
    last = 0
    if csv_path.exists():
        with csv_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                m = re.match(r"ECP(\d+)", row.get("ID", ""))
                if m:
                    last = max(last, int(m.group(1)))
    return last


def append_rows(rows: list[dict], csv_path: Path) -> None:
    """Append rows to the CSV, auto-assigning IDs."""
    next_id = _last_id(csv_path) + 1
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in rows:
            ecp_id = f"ECP{next_id:03d}"
            writer.writerow([
                ecp_id,
                row["name"],
                row["125"],
                row["250"],
                row["500"],
                row["1000"],
                row["2000"],
                row["4000"],
            ])
            print(f"  + {ecp_id}  {row['name']}")
            next_id += 1


# ---------------------------------------------------------------------------
# Playwright scraping
# ---------------------------------------------------------------------------

def fetch_rendered_html(url: str) -> str:
    """Use Playwright/Chromium to fetch fully rendered HTML.

    In notebook kernels, an asyncio loop is typically already running.
    Playwright sync API cannot run inside that loop, so we execute the sync
    browser call in a worker thread in that case.
    """

    def _fetch_sync() -> str:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print(
                "Playwright is not installed. Run:\n"
                "  pip install playwright && playwright install chromium",
                file=sys.stderr,
            )
            sys.exit(1)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)
            # Wait for the table to appear
            try:
                page.wait_for_selector("table.table", timeout=10000)
            except Exception:
                pass
            html = page.content()
            browser.close()
        return html

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No active loop in this thread: normal script/CLI path.
        return _fetch_sync()

    if loop.is_running():
        with ThreadPoolExecutor(max_workers=1) as ex:
            return ex.submit(_fetch_sync).result()

    return _fetch_sync()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scrape_and_append(
    url: str,
    product_line: str,
    csv_path: Path | str = DEFAULT_CSV,
) -> int:
    """Scrape *url*, parse absorption tables and append rows to *csv_path*.

    Returns the number of rows appended.
    """
    csv_path = Path(csv_path)
    print(f"Fetching: {url}")
    html = fetch_rendered_html(url)
    rows = parse_absorption_tables(html, product_line)

    if not rows:
        print("WARNING: no absorption rows found. Check the URL or product line name.")
        return 0

    print(f"Parsed {len(rows)} rows – appending to {csv_path.name}:")
    append_rows(rows, csv_path)
    return len(rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape an Ecophon product page and append to ecophon.csv"
    )
    parser.add_argument("--url", required=True, help="Full URL of the Ecophon product page")
    parser.add_argument("--name", required=True, help='Product line prefix, e.g. "Ecophon Focus A"')
    parser.add_argument(
        "--csv",
        default=str(DEFAULT_CSV),
        help=f"Path to target CSV (default: {DEFAULT_CSV})",
    )
    args = parser.parse_args()
    scrape_and_append(url=args.url, product_line=args.name, csv_path=args.csv)


if __name__ == "__main__":
    _main()
