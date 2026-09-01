import sys
import os
from pathlib import Path
#from notebooks.fcst_HALCYON_prophet import df_produccion
import openpyxl
import pandas as pd
import numpy as np

ROOT = Path().cwd().parents[1]
sys.path.append(str(ROOT))

def create_df_produccion_x_equipo(path_raw, path_output):
    df_produccion = pd.read_excel(path_raw,
        sheet_name = 0,
        engine = "openpyxl")

    df_produccion.columns = df_produccion.columns.str.lower()
    df_produccion.columns = ['ds', 'equipo', 'y', 'capacidad', 'tipo_dia', 'novedad']
    df_produccion['novedad'] = df_produccion['novedad'].fillna('ninguna')
    df_produccion.to_csv(path_output,
        index = False,
        encoding = "utf-8")

    return df_produccion
