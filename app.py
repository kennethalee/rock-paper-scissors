from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from models.models import db, User, Game
import main

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Jancokasu123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.route('/')
def home():
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash('Login to access profile page')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your username and password')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username exists
        if User.query.filter_by(username=username).first():
            flash('Username unavailable')
            return redirect(url_for('register'))

        # Hash password and create new username
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration complete! Log in!')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(current_user.id)
    games = Game.query.filter_by(user_id=user.id).all()
    return render_template('profile.html', user=user, games=games)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/play', methods=['POST'])
def play():
    player_choice = request.form.get('choice')
    computer_choice = main.get_computer_choice()
    result = main.determine_winner(player_choice, computer_choice)

    # Save result to database only if logged in user
    if current_user.is_authenticated:
        new_game = Game(
            user_id=current_user.id,
            player_choice=player_choice,
            computer_choice=computer_choice,
            result=result
        )
        db.session.add(new_game)
        db.session.commit()

    return render_template(
        'result.html', player_choice=player_choice,
        computer_choice=computer_choice, result=result
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
