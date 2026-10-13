from prefect import task
from datetime import datetime
from config.settings import OUTPUT_PATH, days_to_forecast
from src.extract_files import get_demanda_diaria, get_demanda_hist_equipment
from src.filter import train_val_test
import pandas as pd
import os

@task
def transform_data(df_produccion):
    os.makedirs(os.path.dirname(os.path.join(OUTPUT_PATH, "demanda", "train")), exist_ok = True)
    os.makedirs(os.path.dirname(os.path.join(OUTPUT_PATH, "demanda", "test")), exist_ok = True)
    os.makedirs(os.path.dirname(os.path.join(OUTPUT_PATH, "demanda", "validation")),exist_ok = True)

    path_train = os.path.join(OUTPUT_PATH, "demanda", "train")
    path_test = os.path.join(OUTPUT_PATH, "demanda", "test")
    path_val = os.path.join(OUTPUT_PATH, "demanda", "validation")


    path_demanda_hist = get_demanda_hist_equipment(df_produccion)
    df_hist = pd.read_csv(path_demanda_hist)
    days_to_forecast1 = days_to_forecast * 2

    train, val, test, train_dates, val_dates, test_dates = train_val_test(df_hist, days_to_forecast1)


    train.to_csv(os.path.join(path_train,"train_demand_csv"), index = False)
    pd.Series(train_dates, name = "ds").to_csv(os.path.join(
        path_train, "train_dates.csv"), index = False)

    test.to_csv(os.path.join(path_test,"test_demand.csv"), index = False)
    pd.Series(test_dates, name = "ds").to_csv(os.path.join(
        path_test, "test_dates.csv"), index = False)

    val.to_csv(os.path.join(path_val, "validation_demand.csv"), index = False)
    pd.Series(val_dates, name = "ds").to_csv(os.path.join(
        path_val, "val_dates.csv"), index = False)


    path_demanda = os.path.join(OUTPUT_PATH, "demanda")
    return path_demanda

#fecha, equipo, produccion, capacidad, tipo_dia, novedad
