from prefect import task
from datetime import datetime
from config.settings import OUTPUT_PATH
from src.extract_files import get_demanda_diaria, get_demanda_hist_equitment


@task
def transform_data(df_produccion):
  #fecha, equipo, produccion, capacidad, tipo_dia, novedad
    df_hist = get_demanda_hist_equitment(df_produccion)
    df_demanda_diaria = get_demanda_diaria(df_produccion)
    demanda_path = os.path.join(OUTPUT_PATH, "demanda")
    df_demanda_diaria.to_csv(demanda_path / "demanda_diaria_total.csv", index=False)
    df_hist.to_csv(demanda_path / "demanda_diaria_x_equipo.csv", index=False)

    return (demanda_path)
