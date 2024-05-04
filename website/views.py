from flask import Blueprint, render_template, request
from flask_login import current_user
import sqlite3
import pandas as pd
import json
import os

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    # conn = sqlite3.connect('/home/hoangvu/final_project_DE/dags/database.db')
    conn = sqlite3.connect('dags/database.db')
    ids = pd.read_sql_query("SELECT DISTINCT ID FROM StockData", conn)
    print(ids)
    query = f"SELECT ID, Close, Changed, Changed_rate FROM StockData;"
    data = pd.read_sql_query(query, conn)
    data = data.drop_duplicates(subset=['ID'])

    query = "SELECT * FROM StockData WHERE ID = 'AAPL'"
    df = pd.read_sql_query(query, conn)
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        date_from = request.form.get('date-from')
        date_to = request.form.get('date-to')
        print(date_from, date_to)
        if  date_from and date_to:
            query = f"SELECT * FROM StockData WHERE ID = '{ticker}' AND Date >= '{date_from}' AND Date <= '{date_to}'"
        else:
            query = f"SELECT * FROM StockData WHERE ID = '{ticker}'"

        df = pd.read_sql_query(query, conn)
    # Ban-WorkSpace
    def conv_db_to_json(ids):
        conn = sqlite3.connect('dags/database.db')
        query = "SELECT *, Adj_Close * Volume AS volume_dollar FROM StockData;"
        df = pd.read_sql_query(query, conn)
        for id in ids['ID']:
            df_stock = df[df['ID'] == id].drop(columns=['ID', 'Adj_Close', 'Volume', 'Changed', 'Changed_rate'])
            df_stock = df_stock[pd.to_datetime(df_stock['Date']).dt.year >= 2012]
            df_stock.columns = [i.lower() for i in df_stock.columns] 
            json_data = df_stock.to_dict(orient='records')
            output_dir = 'website/static'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, f'{id}.json')
            with open(output_path, 'w') as file:
                json.dump(json_data, file, indent=2)
    conv_db_to_json(ids)
    # End Ban-WorkSpace



    return render_template('home.html', 
                           user=current_user,
                           ids=ids,
                           df=df.head(10),
                           data=data
                           )