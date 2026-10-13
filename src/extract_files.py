import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from config.settings import OUTPUT_PATH

def read_produccion(path_processed: str):
    try:
        df_produccion = pd.read_csv(path_processed)
        #df_produccion.columns = ["ds","equipo","y","capacidad","tipo_dia","novedad"]
        df_produccion["ds"] = pd.to_datetime(df_produccion["ds"])

    except Exception as e:
        raise RuntimeError(f"faile to read Excel file: {e}")

    if df_produccion.empty:
        raise ValueError("Extracted dataframe is empty")

    return df_produccion

def get_demanda_diaria(df_produccion):
    #df_produccion = pd.get_dummies(df_produccion, columns = ["tipo_dia", "novedad"])
    #df_produccion.columns = (
    #    df_produccion.columns
    #    .str.strip()
    #    .str.lower()
    #    .str.replace(r"\s+","_",regex = True)
    #    .str.replace(r"tipo_dia_", "", regex = True)
    #    .str.replace("novedad_", "",regex = False )
    #)
    #df_produccion = df_produccion.drop(columns = ["laboral","ninguna"])

    demanda_diaria = df_produccion.groupby("ds", as_index = False).agg(
        y = ("y", "sum"),
        capacidad = ("capacidad", "sum"),
        festivo = ("festivo", lambda x: x.mode()[0]),
        fin_de_semana = ("fin_de_semana", lambda x: x.mode()[0]),
        control_de_calidad = ("control_de_calidad", lambda x: x.mode()[0]),
        falla = ("falla", lambda x: x.mode()[0]),
        mantenimiento = ("mantenimiento", lambda x: x.mode()[0]),
        )
    demanda_path = os.path.join(OUTPUT_PATH, "demanda")
    file_path = os.path.join(demanda_path, "demanda_diaria_total.csv")

    demanda_diaria.to_csv(file_path, index=False)


    return file_path

def get_demanda_hist_equipment(df_produccion):
    df_hist = df_produccion.copy()
    #tipo_dia_cols = ["festivo", "fin_de_semana", "laboral"]
    #novedad_cols = ["control_calidad", "falla", "manteminient""o"]
    #df_hist = pd.get_dummies(df_hist, columns = ["tipo_dia", "novedad"])

    #df_hist.columns = (
    #    df_hist.columns
    #    .str.strip()
    #    .str.lower()
    #    .str.replace(r"\s+","_",regex = True)
    #    .str.replace(r"tipo_dia_", "", regex = True)
    #    .str.replace("novedad_", "",regex = False )
    #)
    demanda_path = os.path.join(OUTPUT_PATH, "demanda")
    file_path = os.path.join(demanda_path,  "demanda_diaria_x_equipo.csv")
    df_hist.to_csv(file_path , index=False)



    return file_path
