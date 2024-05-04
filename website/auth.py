from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
from datetime import datetime
from .models import User
import yfinance as yf
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Đăng nhập thành công!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Mật khẩu không đúng, thử lại lần nữa', category='error')
        else:
            flash('Tài khoản hiện chưa được đăng ký', category='error')

    data = request.form
    print(data)
    return render_template('login.html', user=current_user)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(username=username).first()

        if user:
            flash('Tài khoản đã tồn tại', category='error')
        elif len(password1) < 5:
            flash('Mật khẩu phải có tối thiểu 5 ký tự', category='error')
        elif password1 != password2:
            flash('Mật khẩu không đồng nhất', category='error')
        else:
            new_user = User(username=username, email=email, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Tạo tài khoản thành công!', category='success')
            login_user(new_user)
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@auth.route('/news')
def news():
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

    items = []

    for ticker in tickers:
        news = yf.Ticker(ticker).get_news()
        for new in news:
            title = new['title']
            publisher = new['publisher']
            link = new['link']
            time = datetime.utcfromtimestamp(new['providerPublishTime']).strftime('%Y-%m-%d %H:%M:%S')
            related_tickers = []
            img_url = ""
                
            if 'relatedTickers' in new:
                related_tickers = new['relatedTickers']
            
            if 'thumbnail' in new:
                img_url = new['thumbnail']['resolutions'][-1]['url']
            
            item = [title, link, publisher, time, img_url, related_tickers]
            if item not in items:
                items.append(item)

    return render_template('news.html', user=current_user, items=items)

@auth.route('/about')
def about():
    return render_template('about.html')