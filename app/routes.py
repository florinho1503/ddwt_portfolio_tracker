from app import app, db
from flask import render_template, request, redirect, url_for, flash
from app.models import User, Transaction, Portfolio
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, RegistrationForm
from datetime import datetime
from .portfolio_analyzer import PortfolioAnalyzer

@app.route('/', methods=['GET'])
# You don't have to log in for the home page, only for the portfolio tracker
def index():
    """Display the list of movies."""
    # movies = Movie.query.all()
    return render_template('index.html')

from app.portfolio_analyzer import PortfolioAnalyzer


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

    return {"live_value": round(live_value, 2)}  # Return as JSON


@app.route('/portfolio_tracker')
@login_required
def portfolio_tracker():
    """Display the user's portfolio and performance."""
    user_id = current_user.id
    analyzer = PortfolioAnalyzer(user_id)

    # Calculate holdings and plot performance
    portfolio_df, latest_values = analyzer.calculate_current_holdings()

    if portfolio_df is None:
        holdings = {}
        live_value = 0
        plot_path = None
    else:
        # Calculate the latest portfolio value
        live_value = portfolio_df["Portfolio Value"].iloc[-1]

        # Calculate percentages for pie chart
        total_value = sum(latest_values.values())
        holdings = {stock: round((value / total_value) * 100, 2) for stock, value in latest_values.items()}

        # Generate the plot
        plot_path = analyzer.plot_portfolio_performance(user_id)

    return render_template(
        'portfolio_tracker.html',
        plot_path=plot_path,
        holdings=holdings,
        live_value=live_value
    )


# Adding Transactions
@app.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """Add a new transaction for the current user's portfolio."""

    # Ensure the user has a portfolio
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        # Automatically create a portfolio for the user if it doesn't exist
        portfolio = Portfolio(user_id=current_user.id, name='Default Portfolio')
        db.session.add(portfolio)
        db.session.commit()
        print(f"Created portfolio for user {current_user.id}: {portfolio}")

    if request.method == 'POST':
        # Debug: Log POST data
        print(f"POST data received: {request.form}")

        transaction_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()

        # Create a new transaction
        transaction = Transaction(
            portfolio_id=portfolio.portfolio_id,  # Automatically associate with the user's portfolio
            stock_ticker=request.form['stock_ticker'],
            quantity=float(request.form['quantity']),
            price=float(request.form['price']),
            date=transaction_date,
            transaction_type=request.form['transaction_type']
        )

        # Save the transaction
        try:
            db.session.add(transaction)
            db.session.commit()
            print("Transaction saved to the database.")
            flash('Transaction saved successfully!')
        except Exception as e:
            db.session.rollback()
            print(f"Error saving transaction: {e}")
            flash('Failed to save transaction.')
            return redirect(url_for('add_transaction'))

        return redirect(url_for('index'))

    # Render the transaction form
    return render_template('add_transaction.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    if current_user.is_authenticated:  # Redirect if already logged in
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():  # Check if the form is submitted and valid
        user = User.query.filter_by(username=form.username.data).first()  # Get user by username
        if user is None or not user.check_password(form.password.data):  # Check credentials
            flash('Invalid username or password.')
            return redirect(url_for('login'))
        
        login_user(user)  # Log the user in
        flash('Login successful!')
        return redirect(url_for('index'))
    
    return render_template('login.html', title='Login', form=form)

from sqlalchemy import text
@app.before_request
def enforce_foreign_keys():
    """Ensure SQLite enforces foreign key constraints."""
    if db.engine.dialect.name == "sqlite":
        db.session.execute(text('PRAGMA foreign_keys=ON;'))

# Logging out
@app.route('/logout')
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if current_user.is_authenticated:  # Redirect if already logged in
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():  # Validate the registration form
        # Create and save the new user to database
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)  # Hash the password
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')

        # Create a portfolio for the new user
        portfolio = Portfolio(user_id=user.id, name="Default Portfolio")
        db.session.add(portfolio)
        db.session.commit()  # Save the portfolio

        flash('Portfolio created successfully! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


# If wrong URL is entered you get directed to error page. This is the custom error handler
@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error handler."""
    return render_template('404.html'), 404

@app.route('/stockwatch') 
def stockwatch():
    return render_template('stockwatch.html')
"""
@app.route('/videos')
def videos():
    return render_template('videos.html')
"""

@app.route('/about')
def about():
    return render_template('about.html')
