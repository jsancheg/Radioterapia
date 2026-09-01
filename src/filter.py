import pandas as pd

def obtiene_equipos(df: pd.DataFrame) -> list:
    equipos = list(df['equipo'].unique())
    return equipos

def obtiene_serie (df: pd.DataFrame, equipo) -> pd.DataFrame:
    df_eq = df[df['equipo'] == equipo].copy()
    cols = ['ds', 'y'] + [ c
        for c in df_eq.columns  if c not in ['ds', 'y', 'equipo', 'tipo_dia']
        ]

    df_eq = df_eq[cols]
    return df_eq

def train_val_test (df: pd.DataFrame, days_to_forecast: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    dates = df["ds"].sort_values().unique()

    train_end = len(dates) - 2*days_to_forecast
    val_end = len(dates) - days_to_forecast

    train_dates = dates[:train_end]
    val_dates = dates[train_end:val_end]
    test_dates = dates[val_end:]


    train = df[df["ds"].isin(train_dates)]
    val = df[df["ds"].isin(val_dates)]
    test = df[df["ds"].isin(test_dates)]

    return train, val, test, train_dates, val_dates, test_dates
