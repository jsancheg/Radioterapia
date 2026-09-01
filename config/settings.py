from pathlib import Path

BASE = Path.cwd().resolve().parent.parent
DATA_DIR = BASE / "data"


OUTPUT_PATH = BASE / "data" / "processed"
path_produccion = DATA_DIR / "processed" / "produccion_radioterapia.csv"
path_raw_file = DATA_DIR / "raw" / "SESIONES_RADIOTERAPIA_5MAY22-30ABR2026.xlsx"
RETRY_DELAY = 5

param_grid = {
    "changepoint_prior_scale": [0.01, 0.1, 0.5],
    "seasonality_prior_Scale": [1, 5, 10] }

}
