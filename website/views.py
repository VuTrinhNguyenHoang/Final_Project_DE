from flask import Blueprint, render_template
from flask_login import current_user

views = Blueprint('views', __name__)

import sqlite3
import pandas as pd
@views.route('/')
def home():
    conn = sqlite3.connect('dags/database.db')
    ids = pd.read_sql_query("SELECT DISTINCT ID FROM StockData", conn)
    query = "SELECT ID, Close, Changed, Changed_rate FROM StockData"
    data = pd.read_sql_query(query, conn)
    data = data.drop_duplicates(subset=['ID'])

    conv_db_to_json(data['ID'].values)

    return render_template('home.html', 
                           user=current_user,
                           data=data,
                           ids=ids
                           )

from datetime import datetime
import yfinance as yf
@views.route('/news')
def news():
    tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN',       # Các công ty trên sàn Nasdaq
        'VIC', 'VHM', 'VNM',                   # Các mã chứng khoán trên sàn Ho Chi Minh Stock Exchange (HOSE)
        'GAS', 'BVH', 'TBC',                   # Các mã chứng khoán trên sàn Hanoi Stock Exchange (HNX)
    ]

    items = []
    today = datetime.today().strftime('%Y-%m-%d')

    for ticker in tickers:
        news = yf.Ticker(ticker).get_news()
        for new in news:
            title = new['title']
            publisher = new['publisher']
            link = new['link']
            time = datetime.utcfromtimestamp(new['providerPublishTime']).strftime('%Y-%m-%d')
            related_tickers = []
            img_url = ""
                
            if 'relatedTickers' in new:
                related_tickers = new['relatedTickers']
            
            if 'thumbnail' in new:
                img_url = new['thumbnail']['resolutions'][-1]['url']
            
            item = [title, link, publisher, time, img_url, related_tickers]
            if item not in items and time == today:
                items.append(item)

    return render_template('news.html', user=current_user, items=items)

from tensorflow.keras.models import load_model
@views.route('technical-analysis')
def technical_analysis():

    return render_template('technical_analysis.html', user=current_user)

import os
import json
def conv_db_to_json(ids):
    conn = sqlite3.connect('dags/database.db')
    query = "SELECT *, Adj_Close * Volume AS volume_dollar FROM StockData;"
    df = pd.read_sql_query(query, conn)
    for id in ids:
        df_stock = df[df['ID'] == id]
        df_stock = df_stock[pd.to_datetime(df_stock['Date']).dt.year >= 2012]
        df_stock.columns = [i.lower() for i in df_stock.columns] 
        json_data = df_stock.to_dict(orient='records')
        output_dir = 'website/static'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, f'{id}.json')
        with open(output_path, 'w') as file:
            json.dump(json_data, file, indent=2)
