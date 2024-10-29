from flask import Flask, render_template, redirect, url_for, request, flash, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from io import StringIO
import csv
import main
from models.models import db, User, Game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Jancokasu123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kenneth.aleee@gmail.com'
app.config['MAIL_PASSWORD'] = 'ctmpoohfwimfkzne'
app.config['MAIL_DEFAULT_SENDER'] = 'kenneth.aleee@gmail.com'

mail = Mail(app)

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
        email = request.form['email']
        password = request.form['password']

        # Check if username, email exists
        if User.query.filter_by(username=username).first():
            flash('Username unavailable.')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Account with this email exists.')
            return render_template('register.html')

        # Hash password and create new username
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration complete! Log in!')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('The reset link is invalid or has expired.')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('reset_password.html', token=token)

        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password)
            db.session.commit()
            flash('Your password has been changed')
            return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:
            token = generate_reset_token(user)
            reset_url = url_for('reset_password', token=token, _external=True)
            send_email(
                to=user.email,
                subject="Request for Password Reset",
                body=f"Click the link to reset your password: {reset_url}"
            )
            flash('A password reset link has been sent to your email.')
        else:
            flash('No account associated with that email.')

        return redirect(url_for('login'))
    return render_template('forgot_password.html')

def generate_reset_token(user):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(user.email, salt='password-reset-salt')

def send_reset_email(user, token):
    reset_url = url_for('reset_password', token=token, _external=True)
    send_email(to=user.email, subject="Password Reset Request", body=f"Click the link to reset your password: {reset_url}")

def send_email(to, subject, body):
    msg = Message(subject, recipients=[to])
    msg.body = body
    mail.send(msg)

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(current_user.id)
    games = Game.query.filter_by(user_id=user.id).order_by(Game.timestamp.desc())
    return render_template('profile.html', user=user, games=games)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/clear_history', methods=["POST"])
@login_required
def clear_history():
    Game.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for('profile'))

@app.route('/export_history', methods=['GET'])
@login_required
def export_history():
    # Current user game history
    games = Game.query.filter_by(user_id=current_user.id).all()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(['Date', 'Player', 'Computer', 'Result'])

    for game in games:
        date = game.timestamp.strftime('%Y-%m-%d')
        writer.writerow([date, game.player_choice, game.computer_choice, game.result])

    output.seek(0)  # move to start of file

    return Response(
        output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=game_history.csv"}
    )

@app.route('/delete_account', methods=["POST"])
@login_required
def delete_account():
    Game.query.filter_by(user_id=current_user.id).delete()
    User.query.filter_by(id=current_user.id).delete()
    db.session.commit()
    flash('Your account has been deleted')
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
