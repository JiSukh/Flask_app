from flask import Blueprint, render_template, flash, redirect, url_for, session, get_flashed_messages
from accounts.forms import RegistrationForm, LoginForm
from markupsafe import Markup
from flask_limiter import Limiter
import config
import re



accounts_bp = Blueprint('accounts', __name__, template_folder='templates')


@accounts_bp.route('/account')
def account():
    return render_template("accounts/account.html")

@accounts_bp.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    #session authentication limit

    session_id = 'login_attempts'

    if session.get(session_id) is None:
        session[session_id] = config.maximum_login_attempt

    #if session id exceeded
    if session.get(session_id) <= 0:
        attempts_exceeded = True  
        reset_link = url_for('accounts.reset_attempts')
        message = Markup(f'You have exceeded the maximum login attempts. <a href="{reset_link}">Click here to reset your attempts</a>.')
        flash(message, category='danger')

    if form.validate_on_submit():

        user = config.User.query.filter_by(email=form.email.data).first()

        # If user exists, verify the password
        if user and user.verify_password(input_password=form.password.data):
            flash('Logged in.', category='success')
            session[session_id] = config.maximum_login_attempt #reset attempts on successful login
            return redirect(url_for('posts.posts'))
        else:
            session[session_id] -= 1
            attempts = session[session_id]


            if form.recaptcha.errors:
                flash('Error with recaptcha, please ensure you complete recapture', category='danger')
            else:
                #increase login atemp value       
                flash(f'Account does not exists or you have entered the wrong password. {attempts} attemp(s) remaining.', category='warning')
        
    if session[session_id] <= 0:
        return render_template('accounts/login.html')
    else:
        return render_template('accounts/login.html', form = form)

@accounts_bp.route('/unlock')
def unlock():
    session_id = 'login_attempts'
    session[session_id] = config.maximum_login_attempt  # Reset attempts
    get_flashed_messages() #removed flashed messages
    flash('Login attempts have been reset. You can try logging in again.', category='success')
    return redirect(url_for('accounts.login'))

@accounts_bp.route('/registration', methods=['GET','POST'])
def registration():

    form = RegistrationForm()

    if form.validate_on_submit():

        #Check if email alreaady exists
        if config.User.query.filter_by(email=form.email.data).first():
        
            flash('Email already exists. ', category="danger")
            return render_template('accounts/registration.html', form=form)

        #Password strength checking

        regex = '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)[a-zA-Z\d\W]{8,15}$'

        if not re.match(regex, form.password.data):
            flash('Password is not strong enough.', category="warning")
            return render_template('accounts/registration.html', form=form)

        #create new user
        new_user = config.User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        )
        #add to db
        config.db.session.add(new_user)
        config.db.session.commit()

        flash('Account Created', category='success')
        return redirect(url_for('accounts.login'))

    return render_template('accounts/registration.html', form=form)



