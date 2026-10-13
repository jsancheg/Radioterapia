from IPython.testing.plugin.simplevars import x
import pandas as pd
import numpy as np
#from numpy.f2py.crackfortran import l
from numpy.linalg import inv
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.covariance import LedoitWolf
from itertools import product


def fit_predict_prophet(train, val, params):

    regressors = [c for c in train.columns if c not in ['ds','y','equipo']]

    m = Prophet(
        weekly_seasonality = True,
        **params
    )

    for r in regressors:
        m.add_regressor(r)

    m.fit(train)

    forecast = m.predict(val)

    return forecast["yhat"].values


def tune_total(train, val, regressors, param_grid):
    train_total = train.groupby("ds")["y"].sum().reset_index()
    val_total = val.groupby("ds")["y"].sum().reset_index()

    train_reg = train.groupby("ds")[regressors].mean().reset_index()
    val_reg = val.groupby("ds")[regressors].mean().reset_index()

    train_total = train_total.merge(train_reg, on = "ds")
    val_total = val_total.merge(val_reg, on = "ds")

    best_params = None
    best_rmse = np.inf

    for cps,sps in product(
        param_grid["changepoint_prior_scale"],
        param_grid["seasonality_prior_scale"]
    ):
        params = {
            "changepoint_prior_scale":cps,
            "seasonality_prior_scale":sps
        }

        pred = fit_predict_prophet(train_total, val_total, params)

        rmse = np.sqrt(mean_squared_error(val_total["y"], pred))

        if rmse < best_rmse:
            best_rmse = rmse
            best_params = params

    return best_params



def bottom_up_models(train_full, best_params, regressors, equipos):
    import pandas as pd
    from prophet import Prophet

    models={}
    residuals=[]
    results=[]

    for eq in equipos:
        df_eq = train_full[train_full["equipo"] == eq].copy()

        # Prophet expexts ds, y + regressors
        df_model = df_eq[["ds","y"] + regressors]

        print(df_model.columns)

        m = Prophet(weekly_seasonality=True, **best_params)


        for r in regressors:
            m.add_regressor(r)

        m.fit(df_model)

        pred = m.predict(df_model)

        res = df_model["y"].values - pred["yhat"].values

        # Store residuals
        residuals.append(res)

        # Store model
        models[eq] = m

        # Build output dataframe
        df_result = pd.DataFrame({
            "ds":df_model["ds"].values,
            "equipo":eq,
            "festivo":df_model["festivo"].values,
            "fin_de_semana":df_model["fin_de_semana"].values,
            "control_de_calidad":df_model["control_de_calidad"].values,
            "falla": df_model["falla"].values,
            "mantenimiento": df_model["mantenimiento"].values,
            "capacidad":df_model["capacidad"].values,
            "y": df_model["y"].values,
            "yhat": pred["yhat"].values,
            "residual":res
        })


        results.append(df_result)


    #combine all equipment
    results_df = pd.concat(results, ignore_index = True)
    results_df["yhat"] = results_df["yhat"].clip(lower = 0)
    results_df["residual"] = results_df["y"] - results_df["yhat"]

    return models, residuals, results_df


def top_down_total(train_full, best_params, regressors):
    train_full = train_full.copy()
    train_full["ds"] = pd.to_datetime(train_full["ds"])

    train_total = train_full.groupby("ds")["y"].sum().reset_index()
    train_reg = train_full.groupby("ds")[regressors].mean().reset_index()

    train_total = train_total.merge(train_reg, on = "ds")

    m_total = Prophet(weekly_seasonality=True, **best_params)

    for r in regressors:
        m_total.add_regressor(r)

    m_total.fit(train_total)

    pred_total_train = m_total.predict(train_total)

    train_total_1 = (train_full.groupby("ds", as_index = False)['y'].sum())
    df_compare = train_total_1.merge(
        pred_total_train[["ds","yhat"]],
        on = "ds",
        how = "inner"
    )

    df_compare = train_total_1.merge(pred_total_train[["ds","yhat"]] , on = "ds", how = "inner")

    df_compare["yhat"] = df_compare["yhat"].clip(lower = 0)
    df_compare["residuals"] = df_compare["y"] - df_compare["yhat"]
    res_total = train_total["y"].values - pred_total_train["yhat"].values

    return pred_total_train, df_compare, res_total, m_total


def cal_residual_matrix(res_total, residuals_ds_equipos, equipos):
    # equipos: it is a numpy array containing the names of the equipos
    labels = ["total"] + list(equipos)
    residual_matrix = np.vstack([res_total] + residuals_ds_equipos)
    residual_matrix = np.nan_to_num(residual_matrix, nan = 0.0)

    df_residuals = pd.DataFrame(residual_matrix, index = labels)
    return residual_matrix, df_residuals


def compute_covariance_matrices(residual_df):
    W = np.cov(residual_df)
    W += np.eye(W.shape[0]) * 1e-6

    lw = LedoitWolf()
    W_shrink = lw.fit(residual_df.T).covariance_
    return W, lw, W_shrink

def summing_matrix(equipos):
    n = len(equipos)
    S = np.vstack(
        [np.ones((1,n)),
            np.eye(n)])
    return S


def fc_bottom_up_test(test_dates, test, m_total, models, equipos, regressors):
    #h = len(test_dates)
    bottom = []
    results = []

    for eq in equipos:
        future = test[test["equipo"] == eq][["ds"] + regressors]
        pred = models[eq].predict(future)
        bottom.append(pred["yhat"].values)

        res = test[test["equipo"] == eq]["y"].values - pred["yhat"].values

        df_result = pd.DataFrame({
        "ds":future["ds"].values,
        "equipo":eq,
        "festivo":future["festivo"].values,
        "fin_de_semana":future["fin_de_semana"].values,
        "control_de_calidad":future["control_de_calidad"].values,
        "falla": future["falla"].values,
        "mantenimiento": future["mantenimiento"].values,
        "capacidad":future["capacidad"].values,
        "y": test[test["equipo"] == eq]["y"].values,
        "yhat": pred["yhat"].values,
        "residual":res
         })


        results.append(df_result)


    #combine all equipment
    results_df = pd.concat(results, ignore_index = True)

    bottom = np.array(bottom)

    # total forecast
    future_total = test.groupby("ds")[regressors].mean().reset_index()
    total_pred = m_total.predict(future_total)["yhat"].values

    # Stack
    Yhat = np.vstack([total_pred, bottom])

    return  results_df, Yhat, total_pred


def mint_reconcile(Yhat, W, S):

    P = S @ inv(S.T @ inv(W) @ S) @ (S.T @ inv(W))
    Ytilde = np.zeros_like(Yhat)

    for t in range(Yhat.shape[1]):
        Ytilde[:, t] = P @ Yhat[:, t]

    return Ytilde
