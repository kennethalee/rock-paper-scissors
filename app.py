from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password_1=hashed_password)
        db.session.add(new_user)
        db.session.commit()

    return render_template('register.html')