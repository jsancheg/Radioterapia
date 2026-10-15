import pandas as pd
import numpy as np
from src.fc_prophet import tune_total, bottom_up_models, top_down_total, fc_bottom_up_test, cal_residual_matrix, compute_covariance_matrices, summing_matrix, mint_reconcile
import os
import sys
import ast
from config.settings import OUTPUT_PATH



def fc_test( path_demanda, m_total, models, equipos, regressors):
    path_test = os.path.join(path_demanda, "test/test_demand.csv")
    test = pd.read_csv(path_test)
    test_dates = sorted(test["ds"].unique())
    path_residuals = os.path.join(OUTPUT_PATH,"residuals/residuals_df.csv")
    path_fc_long_dia_equipo = os.path.join(OUTPUT_PATH,"forecast/fcProphet_top_dpwn_long_dia_equipo.csv")
#    path_fc_conciliado_long_dia_equipo = os.path_join(OUTPUT_PATH,f"forecast/fcProphet_top_dpwn_conciliado_dia_equipo.csv")

    residuals_df = pd.read_csv(path_residuals)

    Wm, lw, Wm_shrink = compute_covariance_matrices(residuals_df)

    S = summing_matrix(equipos)

    results_df, yhat_matrix, total_pred = fc_bottom_up_test(test_dates, test, m_total, models, equipos, regressors)

    Y_mint_shrink = mint_reconcile(yhat_matrix,Wm,S)

    results_df.to_csv(path_fc_long_dia_equipo, index = False)


    return results_df, yhat_matrix, Y_mint_shrink, total_pred
