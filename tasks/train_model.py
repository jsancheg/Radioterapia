import pandas as pd
import numpy as np
from src.fc_prophet import tune_total, bottom_up_models, top_down_total, fc_bottom_up_test, cal_residual_matrix
import os
import sys
import ast
from config.settings import OUTPUT_PATH
#from src.notebooks.top_down_tipo_dia_regressor import forecast

def training(path_demanda):
    param_grid = {
    "changepoint_prior_scale": [0.01, 0.1, 0.5],
    "seasonality_prior_scale": [1, 5, 10] }
    path_file_train = os.path.join(path_demanda, "train/train_demand.csv")
    path_file_val = os.path.join(path_demanda, "validation/validation_demand.csv")
    train = pd.read_csv(path_file_train)
    val = pd.read_csv(path_file_val)
    path_residuals = os.path.join(OUTPUT_PATH, "residuals")
    file_path_residuals = os.path.join(path_residuals, "residuals_df.csv")


    regressors = [c for c in train.columns if c not in ['ds', 'y', 'equipo']]
    with open(os.path.join(path_demanda,"regressors.txt"), "w", encoding = "utf-8") as file:
        file.write(str(regressors))
    best_params = tune_total(train, val, regressors, param_grid)

    train_full = pd.concat([train, val])

    equipos = sorted(train_full["equipo"].unique())

    models, residuals, results = bottom_up_models(train_full,best_params, regressors, equipos)
    # top down total
    pred_total_train, train_total_fc_and_res, res_total, m_total = top_down_total(train_full, best_params, regressors)

    forecast_path = os.path.join(OUTPUT_PATH, "forecast")
    file_path_pred_total = os.path.join(forecast_path, "fcProphet_top_level_pred_train_period.csv")
    file_path_act_pred_res_total = os.path.join(forecast_path, "fcProphet_top_level_pred_actual_res.csv")
    # pred_total_train contain the Prophect forecast at top level
    pred_total_train.to_csv(file_path_pred_total, index = False)

    #train_total_fc_and_res contain the Prophet forecast and actual demand and residuals at top level
    train_total_fc_and_res.to_csv(file_path_act_pred_res_total, index = False)

    residuals_matrix, residuals_df = cal_residual_matrix(res_total, residuals, equipos)

    residuals_df.to_csv(file_path_residuals, index = False)

    return best_params, m_total, models, equipos, regressors, residuals, residuals_matrix, residuals_df, results
