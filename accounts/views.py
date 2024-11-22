from flask import Blueprint, render_template, flash, redirect, url_for, session, get_flashed_messages
from accounts.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, login_required
from markupsafe import Markup
from flask_limiter import Limiter
from utils import roles_required
import pyotp
import config
import re



accounts_bp = Blueprint('accounts', __name__, template_folder='templates')



@accounts_bp.route('/account')
@login_required
def account():
    if current_user:
        return render_template("accounts/account.html", user = current_user)
    else:
        return render_template("accounts/account.html")

@accounts_bp.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    #session authentication limit

    session_id = 'login_attempts'

    if current_user.is_authenticated:
        flash("You are already logged in.", category='info')
        return redirect(url_for('posts.posts'))

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
            ################################testing
            #pin_correct = True
            #mfa_enabled = True
            #################################testing


            pin_correct = user.verify_mfa_pin(input_pin = form.mfa_pin.data)
            mfa_enabled = user.verify_mfa_enabled()
            #verify MFA enabled
            if not mfa_enabled and not pin_correct: #pin not enabled + wrong pin entered
                flash('You have not enabled Multi-Factor Authentication. Please enable first to login.', category='error')
                qrURI = str(pyotp.totp.TOTP(user.mfa_key).provisioning_uri(form.email.data, 'CSC2035 BLOG'))
                return render_template('accounts/setup_mfa.html', secret=user.mfa_key, URI = qrURI)
            elif mfa_enabled and not pin_correct: #if pin is incorrect
                flash('Incorrect pin entered', category='error')
                return render_template('accounts/login.html', form = form)
            else: #if pin correct
                login_user(user)
                flash(f'Logged in.', category='success')
                #if MFa not enabled, set to true of successful login.
                if not user.verify_mfa_enabled():
                    user.mfa_enable = True
                    config.db.session.commit()
                session[session_id] = config.maximum_login_attempt #reset attempts on successful login

                #Check user privilegedes
                if current_user.role == 'db_admin':
                    return redirect('http://127.0.0.1:5000/admin')
                elif current_user.role == 'sec_admin':
                    return render_template('security/security.html')
                elif current_user.role == 'end_user':#
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

    if current_user.is_authenticated:
        flash("You are already logged in.", category='info')
        return redirect(url_for('posts.posts'))

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
                        mfa_key= pyotp.random_base32(),
                        mfa_enable = False
                        )
        #add to db
        config.db.session.add(new_user)
        config.db.session.commit()

        

        flash('Account Created. You must set up Multi-Factor Authentication to login.', category='success')
        qrURI = str(pyotp.totp.TOTP(new_user.mfa_key).provisioning_uri(form.email.data, 'CSC2035 BLOG'))
        return render_template('accounts/setup_mfa.html', secret=new_user.mfa_key, URI = qrURI)

    return render_template('accounts/registration.html', form=form)



