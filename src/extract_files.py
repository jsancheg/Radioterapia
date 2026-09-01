import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

def read_produccion(path_processed: str):
    try:
        df_produccion = pd.read_csv(path_processed)
        df_produccion.columns = ["ds","equipo","y","capacidad","tipo_dia","novedad"]
        df_produccion["ds"] = pd.to_datetime(df_produccion["ds"])

    except Exception as e:
        raise RuntimeError(f"faile to read Excel file: {e}")

    if df_produccion.empty:
        raise ValueError("Extracted dataframe is empty")

    return df_produccion

def get_demanda_diaria(df_produccion):
    demanda_diaria = df_produccion[
        ["ds", "y", "capacidad", "tipo_dia", "novedad"]
    ].groupby("ds", as_index = False).agg(
        tipo_dia = ("tipo_dia", lambda x: x.mode()[0]),
        novedad = ("novedad", lambda x: x.mode()[0]),
        y = ("y", "sum"),
        capacidad = ("capacidad", "sum"),
    )
    tipo_dia_cols = ["festivo", "fin_de_semana", "laboral"]
    novedad_cols = ["control_calidad", "falla", "mantenimiento"]
    demanda_diaria = pd.get_dummies(demanda_diaria, columns = ["tipo_dia", "novedad"])

#    for col in tipo_dia_cols + novedad_cols:
#        if col not in demanda_diaria:
#            demanda_diaria[col] = 0

    demanda_diaria.columns = (
        demanda_diaria.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\s+","_",regex = True)
        .str.replace(r"tipo_dia_", "", regex = True)
        .str.replace("novedad_", "",regex = False )
    )

    return demanda_diaria

def get_demanda_hist_equipment(df_produccion):
    df_hist = df_produccion.copy()
    tipo_dia_cols = ["festivo", "fin_de_semana", "laboral"]
    novedad_cols = ["control_calidad", "falla", "manteminiento"]
    df_hist = pd.get_dummies(df_hist, columns = ["tipo_dia", "novedad"])

    df_hist.columns = (
        df_hist.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\s+","_",regex = True)
        .str.replace(r"tipo_dia_", "", regex = True)
        .str.replace("novedad_", "",regex = False )
    )


    return df_hist
