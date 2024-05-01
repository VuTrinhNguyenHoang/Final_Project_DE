from flask import Blueprint, render_template, request
from flask_login import current_user
import sqlite3
import pandas as pd

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    conn = sqlite3.connect('/home/hoangvu/final_project_DE/dags/database.db')
    ids = pd.read_sql_query("SELECT DISTINCT ID FROM StockData", conn)
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

    return render_template('home.html', 
                           user=current_user,
                           ids=ids,
                           df=df.head(10),
                           data=data
                           )