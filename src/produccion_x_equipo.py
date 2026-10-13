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

    df_produccion = pd.get_dummies(df_produccion, columns = ["tipo_dia", "novedad"])
    df_produccion.columns =(
        df_produccion.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\s+","_",regex=True)
        .str.replace(r"tipo_dia_","",regex=True)
        .str.replace("novedad_","",regex=False)
    )

    range_dates = pd.date_range(df_produccion["ds"].min(),df_produccion["ds"].max(), freq = "D")
    equipos = sorted(df_produccion["equipo"].unique())

    complete_index = pd.MultiIndex.from_product(
        [range_dates, equipos],
        names = ["ds", "equipo"]
    )

    df_produccion = (df_produccion.set_index(["ds", "equipo"])
        .reindex(complete_index)
        .reset_index()
    )
    df_produccion = df_produccion.drop(columns = ["laboral", "ninguna"])

    df_produccion["capacidad"] = (
        df_produccion.groupby("equipo") ["capacidad"]
        .ffill()
        .bfill()
        .fillna(0)
        .astype(int)
    )

    df_produccion["y"] = (
        df_produccion.groupby("equipo") ["y"]
        .ffill()
        .bfill()
        .fillna(0)
        .astype(int)
    )

    for col in ["festivo", "fin_de_semana", "control_de_calidad", "falla", "mantenimiento"]:
        if col in df_produccion.columns:
            df_produccion[col] = df_produccion[col].astype("boolean").fillna(False).astype(bool)


    df_produccion.to_csv(path_output,
        index = False,
        encoding = "utf-8")

    return df_produccion
