from prefect import task
from pathlib import Path
from config.settings import BASE, DATA_DIR, OUTPUT_PATH, RETRIES, RETRY_DELAY, path_raw_file, path_produccion
from src.produccion_x_equipo import create_df_produccion_x_equipo
from src.extract_files import read_produccion
import pandas as pd

@task(retries  = RETRIES, retry_delay_seconds = RETRY_DELAY)
def extract_data():
    df_produccion = read_produccion(path_produccion)


    return df_produccion
