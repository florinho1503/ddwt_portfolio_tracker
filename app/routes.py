from app import app, db
from flask import render_template, request, redirect, url_for, flash, jsonify
from app.models import User, Transaction, Portfolio
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, RegistrationForm
from datetime import datetime
from .portfolio_analyzer import PortfolioAnalyzer
from sqlalchemy import text
from .data_fetching import fetch_historical_data

@app.route('/', methods=['GET'])
def index():
    """Display the list of movies."""
    return render_template('index.html')

@app.route('/live_value')
@login_required
def get_live_value():
    """Return the latest live portfolio value."""
    user_id = current_user.id
    analyzer = PortfolioAnalyzer(user_id)

    portfolio_df, _ = analyzer.calculate_current_holdings()

    if portfolio_df is None:
        live_value = 0
    else:
        live_value = portfolio_df["Portfolio Value"].iloc[-1]

    return {"live_value": round(live_value, 2)}

@app.route('/portfolio_tracker')
@login_required
def portfolio_tracker():
    """Display the user's portfolio and performance."""
    user_id = current_user.id
    analyzer = PortfolioAnalyzer(user_id)

    portfolio_df, latest_values = analyzer.calculate_current_holdings()

    if portfolio_df is None:
        holdings = {}
        live_value = 0
        plot_path = None
    else:
        live_value = portfolio_df["Portfolio Value"].iloc[-1]
        total_value = sum(latest_values.values())
        holdings = {stock: round((value / total_value) * 100, 2) for stock, value in latest_values.items()}
        plot_path = analyzer.plot_portfolio_performance(user_id)

    return render_template(
        'portfolio_tracker.html',
        plot_path=plot_path,
        holdings=holdings,
        live_value=live_value
    )

@app.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """Add a new transaction for the current user's portfolio."""
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        portfolio = Portfolio(user_id=current_user.id, name='Default Portfolio')
        db.session.add(portfolio)
        db.session.commit()

    if request.method == 'POST':
        transaction_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        transaction = Transaction(
            portfolio_id=portfolio.portfolio_id,
            stock_ticker=request.form['stock_ticker'],
            quantity=float(request.form['quantity']),
            price=float(request.form['price']),
            date=transaction_date,
            transaction_type=request.form['transaction_type']
        )
        try:
            db.session.add(transaction)
            db.session.commit()
            flash('Transaction saved successfully!')
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to save transaction: {e}')
        return redirect(url_for('index'))

    return render_template('add_transaction.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('login'))
        login_user(user)
        flash('Login successful!')
        return redirect(url_for('index'))
    return render_template('login.html', title='Login', form=form)

@app.before_request
def enforce_foreign_keys():
    """Ensure SQLite enforces foreign key constraints."""
    if db.engine.dialect.name == "sqlite":
        db.session.execute(text('PRAGMA foreign_keys=ON;'))


@app.route('/logout')
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        portfolio = Portfolio(user_id=user.id, name="Default Portfolio")
        db.session.add(portfolio)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error handler."""
    return render_template('404.html'), 404

@app.route('/stockwatch')
def stockwatch():
    return render_template('stockwatch.html')

@app.route('/about')
def about():
    return render_template('about.html')

# API Endpoints
@app.route('/api/portfolio', methods=['GET'])
@login_required
def get_portfolio_summary():
    """Fetch portfolio summary"""
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        return jsonify({'error': 'No portfolio found for this user.'}), 404

    transactions = Transaction.query.filter_by(portfolio_id=portfolio.portfolio_id).all()
    if not transactions:
        return jsonify({'total_value': 0, 'transaction_count': 0}), 200

    holdings = {}
    for t in transactions:
        if t.stock_ticker not in holdings:
            holdings[t.stock_ticker] = 0
        if t.transaction_type.lower() == 'buy':
            holdings[t.stock_ticker] += t.quantity
        elif t.transaction_type.lower() == 'sell':
            holdings[t.stock_ticker] -= t.quantity

    historical_data = {}
    for ticker in holdings.keys():
        if holdings[ticker] > 0:
            historical_data[ticker] = fetch_historical_data(ticker)['Close']

    total_value = 0
    for ticker, qty in holdings.items():
        if qty > 0 and ticker in historical_data:
            latest_price = historical_data[ticker].iloc[-1]
            total_value += qty * latest_price

    return jsonify({
        'portfolio_id': portfolio.portfolio_id,
        'total_value': round(total_value, 2),
        'transaction_count': len(transactions),
    })

@app.route('/api/portfolio/transactions', methods=['GET'])
@login_required
def get_transactions():
    """Fetch all transactions."""
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        return jsonify({'error': 'No portfolio found for this user.'}), 404

    transactions = Transaction.query.filter_by(portfolio_id=portfolio.portfolio_id).all()
    transactions_data = [
        {
            'id': t.id,
            'stock_ticker': t.stock_ticker,
            'quantity': t.quantity,
            'price': t.price,
            'date': t.date.strftime('%Y-%m-%d'),
            'transaction_type': t.transaction_type
        } for t in transactions
    ]

    return jsonify(transactions_data)

@app.route('/api/portfolio/holdings', methods=['GET'])
@login_required
def get_holdings():
    """Fetch holdings and their ticker"""
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        return jsonify({'error': 'No portfolio found for this user.'}), 404

    transactions = Transaction.query.filter_by(portfolio_id=portfolio.portfolio_id).all()
    holdings = {}
    for t in transactions:
        if t.stock_ticker not in holdings:
            holdings[t.stock_ticker] = 0
        holdings[t.stock_ticker] += t.quantity if t.transaction_type.lower() == 'buy' else -t.quantity

    holdings = {ticker: qty for ticker, qty in holdings.items() if qty > 0}

    return jsonify(holdings)

@app.route('/api/portfolio/transaction', methods=['POST'])
@login_required
def add_transaction_api():
    """Add a new transaction via API."""
    data = request.get_json()
    required_fields = ['stock_ticker', 'quantity', 'price', 'date', 'transaction_type']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        portfolio = Portfolio(user_id=current_user.id, name='Default Portfolio')
        db.session.add(portfolio)
        db.session.commit()

    try:
        transaction_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

        transaction = Transaction(
            portfolio_id=portfolio.portfolio_id,
            stock_ticker=data['stock_ticker'],
            quantity=float(data['quantity']),
            price=float(data['price']),
            date=transaction_date,
            transaction_type=data['transaction_type'].upper()
        )
        db.session.add(transaction)
        db.session.commit()
        return jsonify({'message': 'Transaction added successfully.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
