# -*- coding: utf-8 -*-
"""forecasting _api.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mTjhb2HeBRmvyiQDHUdMySKSYTAGaKVo
"""

!pip install kaggle

!mkdir ~/.kaggle

! cp kaggle.json ~/.kaggle/

! chmod 600 ~/.kaggle/kaggle.json

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 22})

from prophet import Prophet
import kaggle
import os

def download_kaggle_dataset(kaggle_dataset: str ="pratyushakar/rossmann-store-sales") -> None:
    api = kaggle.api
    print(api.get_config_value('didihbabs@gmial.com'))
    kaggle.api.dataset_download_files(kaggle_dataset, path="./", unzip=True, quiet=False)

def prep_store_data(df: pd.DataFrame, store_id: int=4, store_open: int=1) -> pd.DataFrame:
  df["Date"] = pd.to_datetime(df['Date'])
  df.rename(columns={'Date':'ds', 'Sales': 'y'}, inplace=True)
  df_store = df[
      (df['Store'] == store_id) &\
      (df['Open'] == store_open)].reset_index(drop=True)
  return df_store.sort_values('ds', ascending=True)

def plot_store_data(df: pd.DataFrame)->None:
  plt.rcParams.update({'font.size':22})
  fig, ax = plt.subplot(figsize=(20,10))
  df.plot(x='ds', y='y', ax=ax)
  ax.set_xlabel('Date')
  ax.set_ylabel('Volume')
  ax.legend(['Truth'])
  current_ytick_values = plt.gca().get_yticks()
  plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_ytick_values])

def train_predict(df:pd.DataFrame, train_fraction:float, seasonality:dict)-> tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, int]:

    # grab split data
    train_index = int(train_fraction*df.shape[0])
    df_train = df.copy().iloc[0:train_index]
    df_test = df.copy().iloc[train_index:]

    model = Prophet(
        yearly_seasonality= seasonality['yearly'],
        weekly_seasonality= seasonality['weekly'],
        daily_seasonality= seasonality['daily'],
        interval_width = 0.95
    )

    model.fit(df_train)
    predicted = model.predict(df_test)
    return predicted, df_train, df_test, train_index

def plot_forecast(df_train: pd.DataFrame, df_test: pd.DataFrame, predicted: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(20,10))
    df_test.plot(
        x='ds',
        y='y',
        ax=ax,
        label='Truth',
        linewidth=1,
        markersize=5,
        color='tab:blue',
        alpha=0.9,
        marker='o'
    )
    predicted.plot(
        x='ds',
        y='yhat',
        ax=ax,
        label='Prediction',
        linewidth=2,
        markersize=5,
        color='k'
    )
    ax.fill_between(
        x=predicted['ds'],
        y1=predicted['yhat_upper'],
        y2=predicted['yhat_lower'],
        alpha=0.1,
        color='k'
    )
    df_train.iloc[train_index-100:].plot(
        x='ds',
        y='y',
        ax=ax,
        color='tab:blue',
        label='_nolegend_',
        alpha=0.5,
        marker='o'
    )

    current_ytick_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_ytick_values])
    ax.set_xlabel('Date')
    ax.set_ylabel('Sales')
    plt.savefig('store_data_forecast.png')

if __name__ == "__main__":
  file_path = 'train.csv'
  if os.path.exists(file_path):
    df =pd.read_csv(file_path)
  else:
    download_kaggle_dataset()
    df = pd.read_csv(file_path)

df = prep_store_data(df)

seasonality = {
    'yearly': True,
    'weekly': True,
    'daily': False

}

predicted, df_trian, df_test, train_index = train_predict(
    df=df, train_fraction = 0.8,
    seasonality=seasonality

)

plot_forecast(df_trian, df_test, predicted)