from flask import Blueprint, render_template
import sqlite3
import pandas as pd

views = Blueprint('views', __name__)

@views.route('/')
def home():
    conn = sqlite3.connect('database.db')
    query = f"SELECT DISTINCT ID FROM StockData;"
    df = pd.read_sql_query(query, conn)
    return render_template('home.html', df=df)