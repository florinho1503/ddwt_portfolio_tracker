from app import app, db
from flask import render_template, request, redirect, url_for, flash
from app.models import Movie, User
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, RegistrationForm

# Reinout Vrielink - S5703166
# Index/Home page
@app.route('/', methods=['GET'])
# You don't have to log in for the home page, only for the portfolio tracker
def index():
    """Display the list of movies."""
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

# Adding Movies
@app.route('/add_movie', methods=['GET', 'POST'])
@login_required  # By adding this you get directed to the login screen if you haven't logged in
def add_movie():
    """Add a new movie or update an existing one."""
    movie = None
    if request.method == 'POST':
        movie_id = request.form.get('id')
        if movie_id:
            # Update existing movie
            movie = Movie.query.get(movie_id)
            if movie:
                movie.name = request.form['name']
                movie.year = request.form['year']
                movie.oscars = request.form['oscars']
            else:
                return "Movie not found.", 404
        else:
            # Add a new movie
            movie = Movie(
                name=request.form['name'],
                year=request.form['year'],
                oscars=request.form['oscars']
            )
        # Save changes to the database
        db.session.add(movie)
        db.session.commit()
        flash('Movie saved successfully!')
        return redirect(url_for('index'))
    
    movie_id = request.args.get('id')
    if movie_id:
        movie = Movie.query.get(movie_id)
    return render_template('add_movie.html', movie=movie)

# Deleting a movie
@app.route('/delete_movie/<int:id>', methods=['POST'])
@login_required  # Again, login required. Users can only view, edit, delete and add new movies after logging in
def delete_movie(id):
    """Delete a movie by its ID."""
    movie_to_delete = Movie.query.get_or_404(id)
    try:
        db.session.delete(movie_to_delete)
        db.session.commit()
        flash('Movie deleted successfully!')
        return redirect(url_for('index'))
    except Exception as e:
        return f"There was a problem deleting that movie: {e}"

# Logging in
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

# Logging out
@app.route('/logout')
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

# Registering
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
        flash('Registration successful! Please log in.')
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

@app.route('/portfolio_tracker')
@login_required
def portfolio_tracker():
    return render_template('portfolio_tracker.html')
