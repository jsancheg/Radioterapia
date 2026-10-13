from prefect import flow

from tasks.extract import extract_data
from tasks.transform import transform_data
from tasks.train_model import training
from tasks.forecast_test_subset import fc_test

@flow(name = "Demand Prophet Pipeline")
def demand_pipeline():

    df_produccion = extract_data()
    path_demanda = transform_data(df_produccion)
    best_params, m_total, models, equipos, regressors, residuals, residuals_matrix, residuals_df, results = training(path_demanda)

    results_df, yhat_matrix, Y_mint_shrink, total_pred = fc_test(path_demanda, m_total, models, equipos, regressors)


if __name__ == "__main__":
    demand_pipeline()
