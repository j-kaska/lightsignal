"""
LightSignal — generate_h3_grid.py
====================================
Creates the full H3 grid for the contiguous United States at resolutions
3, 4, and 5. Every cell in the CONUS bounding box is included with all
data columns initialized to 0. This grid is the starting point for the
H3 pipeline — DC, PP, and build cost scripts then fill in their values.

Running this script first ensures that:
  - Every US cell appears in the dashboard (blank = confirmed zero, not missing data)
  - DC and PP scripts update cells rather than creating them, keeping the grid stable
  - The map reads as a true choropleth with a visible dark baseline

Run directly:
  python scripts/h3/generate_h3_grid.py

Or called automatically by:
  python scripts/run_all.py
"""

import sys
import logging
from pathlib import Path

import pandas as pd
from utils.h3_utils import polyfill_box, h3_version

# ── Path setup ────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
ROOT       = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from utils.config import (
    H3_FILES, H3_RESOLUTIONS,
    H3_COL_ID,
    H3_COL_DC_OPERATIONAL, H3_COL_DC_PIPELINE, H3_COL_DC_TOTAL,
    H3_COL_PP_OPERATIONAL, H3_COL_PP_PLANNED, H3_COL_PP_TOTAL,
)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Contiguous US bounding box ────────────────────────────────────────────────
# Covers all 48 contiguous states. A small number of cells will fall over
# coastal waters or border areas — they will display as zero/baseline grey.
CONUS_SOUTH =  24.396308   # Florida Keys
CONUS_NORTH =  49.384358   # Northwest Angle, MN
CONUS_WEST  = -124.848974  # Cape Flattery, WA
CONUS_EAST  =  -66.885444  # West Quoddy Head, ME

# Columns initialized to 0 in the base grid.
# Build cost (bc_unit_cost_ft) is NOT included here — it's added later by
# generate_h3_build_cost.py which fills missing cells with the median cost.
DATA_COLUMNS = [
    H3_COL_DC_OPERATIONAL,
    H3_COL_DC_PIPELINE,
    H3_COL_DC_TOTAL,
    H3_COL_PP_OPERATIONAL,
    H3_COL_PP_PLANNED,
    H3_COL_PP_TOTAL,
]


def generate_h3_grid():
    log.info("=" * 55)
    log.info("  LightSignal — H3 Grid Generation (CONUS baseline)")
    log.info("=" * 55)
    log.info(f"  h3 library version: {h3_version()}")
    log.info(f"  Bounding box: ({CONUS_SOUTH}°N, {CONUS_WEST}°W) → "
             f"({CONUS_NORTH}°N, {CONUS_EAST}°W)")

    for res in H3_RESOLUTIONS:
        log.info(f"  Generating resolution {res}...")

        # Get all H3 cells covering the CONUS bounding box
        cells = polyfill_box(CONUS_SOUTH, CONUS_WEST, CONUS_NORTH, CONUS_EAST, res)

        # Build DataFrame — all data columns start at 0
        df = pd.DataFrame({H3_COL_ID: sorted(cells)})
        for col in DATA_COLUMNS:
            df[col] = 0.0

        # Write — this overwrites any existing h3_r*.csv so we start clean
        filepath = H3_FILES[res]
        filepath.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(filepath, index=False, encoding="utf-8")

        log.info(f"    Resolution {res}: {len(df):,} cells → {filepath.name}")

    log.info("H3 grid generation complete.")


if __name__ == "__main__":
    generate_h3_grid()
