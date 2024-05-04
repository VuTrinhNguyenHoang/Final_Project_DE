from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator

import datetime as dt
import pandas as pd
import pymongo
import random
import time
import os

import subprocess
import sqlite3
import yfinance as yf

tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN',        # Các công ty trên sàn Nasdaq
        'DIS', 'JPM', 'WMT', 'KO',              # Các công ty trên sàn New York Stock Exchange (NYSE)
        '7203.T', '6758.T', '9984.T',           # Các công ty trên sàn Tokyo Stock Exchange (TSE)
        'HSBA.L', 'BP.L',                      # Các công ty trên sàn London Stock Exchange (LSE)
        '^DJI', '^GSPC', '^IXIC',              # Các chỉ số chứng khoán
        'VIC', 'VHM', 'VNM',                   # Các mã chứng khoán trên sàn Ho Chi Minh Stock Exchange (HOSE)
        'GAS', 'BVH', 'TBC',                   # Các mã chứng khoán trên sàn Hanoi Stock Exchange (HNX)
        '9988.HK', 'TSLA', '7203.T', 'VOW3.DE' # Các công ty trên các sàn chứng khoán khác
    ]

def _crawl_data():
    for ticker in tickers:
        data = yf.download(ticker)
        data = data.sort_index(ascending=False)
       
        data.to_csv(ticker + '.csv')
    print('Successfully.')
    return True

def _clean_data():
    for ticker in tickers:
        data = pd.read_csv(ticker + '.csv')
        h, _ = data.shape
        ls = []
        ls_rate = []
        for i in range(h):
            if i == (h - 1):
                ls.append(0)
                ls_rate.append(0)
                break
            ls.append(round(data.iloc[i][4] - data.iloc[i + 1][4], 2))
            ls_rate.append(str(round(ls[i] / data.iloc[i + 1][4] * 100, 2)) + '%')

        data = data.assign(Changed=ls)
        data = data.assign(Changed_rate=ls_rate)
        data.to_csv(ticker + '.csv')
    print('Successfully.')
    return True

def insert_to_sqlite():
    os.remove('/opt/airflow/dags/database.db')
    conn = sqlite3.connect('/opt/airflow/dags/database.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS StockData (
            ID TEXT,
            Date DATE,
            Open REAL,
            High REAL,
            Low REAL,
            Close REAL,
            Adj_Close REAL,
            Volume INTEGER,
            Changed REAL,
            Changed_rate TEXT
        );
    """)

    for ticker in tickers:
        data = pd.read_csv(ticker + '.csv')
        
        for _, row in data.iterrows():
            date = pd.to_datetime(row['Date']).date()
            cursor.execute("""
                INSERT INTO StockData (ID, Date, Open, High, Low, Close, Adj_Close, Volume, Changed, Changed_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ticker, date, round(row['Open'], 2), round(row['High'], 2), 
                  round(row['Low'], 2), round(row['Close'], 2), round(row['Adj Close'], 2), 
                  round(row['Volume'], 2), row['Changed'], row['Changed_rate']))

    print('Successfully.')
    conn.commit()
    conn.close()

def get_data_from_sqlite3():
    conn = sqlite3.connect('/opt/airflow/dags/database.db')
    start_date = '2024-04-01'
    end_date = '2024-04-30'

    query = f"SELECT * FROM StockData WHERE date >= '{start_date}' AND date <= '{end_date}' AND ID = '{'AAPL'}'"

    df = pd.read_sql_query(query, conn)
    print(df)
    conn.close()
    print('Successfully.')


default_args = {
    "owner": "HA",
    'email': ['ha20040204@gmail.com'],
    'email_on_failure': True,
    "start_date": dt.datetime.now() - dt.timedelta(minutes=2),
    "retries": 1,
    "retry_delay": dt.timedelta(minutes=1),
}

with DAG("Final_exam",
    default_args=default_args,
    tags=['Test'],
    schedule_interval = '@once' # 
) as dag:

    starting = BashOperator(task_id = 'starting', bash_command = 'echo "Chuẩn bị cào dữ liệu"')

    create_file= BashOperator(task_id='create_file_task', bash_command='touch /opt/airflow/dags/database.db',)

    crawl_data = PythonOperator(task_id = 'craw_data', python_callable = _crawl_data)

    clean_data = PythonOperator(task_id = 'clean_data', python_callable = _clean_data)

    insert_db = PythonOperator(task_id = 'insert_db', python_callable = insert_to_sqlite)

    get_data = PythonOperator(task_id = 'get_data', python_callable = get_data_from_sqlite3)

    ending = BashOperator(task_id = 'ending', bash_command = 'echo "Completed"')


starting >> [crawl_data, create_file] >> clean_data >> insert_db >> get_data >> ending