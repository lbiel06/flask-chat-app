# Flask + SocketIO Chat-App v3.3
# @leonardbielka


import datetime
import bcrypt
import string
from flask import redirect, render_template, request, session, url_for
from flask_socketio import disconnect, emit, join_room, leave_room
from sqlalchemy import tuple_
from . import app, db, socketio
from . import models


# Form validation settings
USERNAME_ALLOWED_CHARACTERS = string.ascii_letters + string.digits + '_'
USERNAME_MIN_LENGHT = 3
USERNAME_MAX_LENGHT = 15
PASSWORD_MIN_LENGHT = 3
PASSWORD_MAX_LENGTH = 20
MESSAGE_MAX_LENGHT = 100
LOGIN_ON_REGISTRATION = True


# Client side session configuration
# if PERMANENT_SESSION:
#     @app.before_request
#     def make_session_permanent():
#         session.permanent = True
        

# Jinja filter for formatting date

@app.template_filter('format_date')
def format_date(date):
    return date.strftime('%d.%m.%y %H:%M')


# Authentication tools

def is_authenticated() -> bool:
    return 'username' in session


def get_username() -> str:
    # Make sure user is authenticated
    return session['username']


def login_user(username: str) -> None:
    session['username'] = username


def logout_user() -> None:
    # Make sure user is authenticated
    session.pop('username')
    

# Form validators

...


# SocketIO event handlers

@socketio.on('connect')
def connect():
    if is_authenticated():
        join_room(get_username())
        
        # Update user status
        models.User.query.get(get_username()).online = True
        db.session.commit()
        print(get_username(), 'connected')

    else:
        disconnect()


@socketio.on('message')
def message(data):
    if is_authenticated():
        to = data.get('to')
        text = data.get('text')
        
        # Make sure message lenght is within limit
        if 0 < len(text) <= MESSAGE_MAX_LENGHT:
            date = datetime.datetime.now()

            # Make sure username is valid
            if models.User.query.get(to):
                
                # Create message object
                new_message = models.Message(get_username(), to, text, date)
                db.session.add(new_message)
                db.session.commit()
                
                # Avoid sending message twice if
                # user sends message to himself
                users = [get_username()]
                if to != users[0]:
                    users.append(to)

                # Send message
                for room in users:
                    emit('message', {
                        'from': get_username(),
                        'to': to,
                        'text': text,
                        'date': format_date(date)
                    }, room=room)

                print(new_message)
                

@socketio.on('disconnect')
def disconnect():
    if is_authenticated():
        leave_room(get_username())
        # Update user status
        models.User.query.get(get_username()).online = False
        db.session.commit()
        print(get_username(), 'disconnected')


# Flask request handlers

@app.route('/')
def home():
    if is_authenticated():
        # Redirect to chat with first user in alphabetical order
        default_user = models.User.query.order_by(models.User.username).first()
        # return redirect(url_for('chat', username=default_user.username))
        # Url bug fix
        return redirect(f'/@/{default_user.username}')
    
    return redirect(url_for('login'))


@app.route('/@/<username>')
def chat(username):
    if is_authenticated():
        # Make sure username is valid
        if models.User.query.get(username):
            users = models.User.query.order_by(models.User.username).all()
            # Get all messages sent to user or
            # received by user, ordered by date.
            messages = models.Message.query.filter(
                tuple_(models.Message.from_, models.Message.to).in_(
                    [
                        temp := (get_username(), username),
                        # (username, get_username())
                        temp[::-1]
                    ]
                )
            ).order_by(models.Message.date.asc()).all()
            print('messages:', messages)
            return render_template('chat2.html', to=username, messages=messages, users=users)

    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    else:
        username = request.form.get('username')
        password = request.form.get('password')
        remember_user = request.form.getlist('remember-user')
        
        print(request.form.getlist('remember-user'))
        # Form validation + error messages
        
        error_messages = []
        
        if not all([username, password]):
            return render_template('login.html')
        
        if not (user := models.User.query.get(username)):
            error_messages.append('Invalid username')

        if not error_messages:
            # Check password
            correct_password_hash = user.password_hash
            
            if bcrypt.checkpw(password.encode(), correct_password_hash):
                if remember_user:
                    session.permanent = True
                login_user(username)
                print(user)
                return redirect(url_for('home'))
            
            else:
                error_messages.append('Invalid password')

        return render_template('login.html', error_messages=error_messages)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    else:
        username = request.form.get('username')
        password1 = request.form.get('password-1')
        password2 = request.form.get('password-2')
        
        error_messages = []
        
        # Form validation + error messages

        if not USERNAME_MIN_LENGHT <= len(username) <= USERNAME_MAX_LENGHT:
            error_messages.append(f'Username must be {USERNAME_MIN_LENGHT} to {USERNAME_MAX_LENGHT} characters long')
            
        if not all(character in USERNAME_ALLOWED_CHARACTERS for character in username):
            error_messages.append('Username can contain only letters, digits, and underscores')

        if password1 != password2:
            error_messages.append('Passwords don\'t match')
            
        if not PASSWORD_MIN_LENGHT <= len(password1) <= PASSWORD_MAX_LENGTH:
            error_messages.append(f'Password must be {PASSWORD_MIN_LENGHT} to {PASSWORD_MAX_LENGTH} characters long')

        if models.User.query.get(username):
            error_messages.append('Username is already taken')

        if not error_messages:
            # Create user
            new_password_hash = bcrypt.hashpw(password1.encode(), bcrypt.gensalt())
            new_user = models.User(username, new_password_hash)
            db.session.add(new_user)
            db.session.commit()
            print(new_user)
            
            # Automatically login user if
            # LOGIN_ON_REGISTRARION set to True
            if LOGIN_ON_REGISTRATION:
                login_user(username)
                return redirect(url_for('home'))
            
            else:
                return redirect(url_for('login'))

        return render_template('register.html', error_messages=error_messages)


@app.route('/logout')
def logout():
    if is_authenticated():
        logout_user()
    
    return redirect('/login')
