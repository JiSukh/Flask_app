from flask import Blueprint, render_template, flash, redirect, url_for, session, request, get_flashed_messages
from accounts.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, login_required, logout_user
from markupsafe import Markup
from utils import Sym_Encryption

import argon2
import pyotp
import re
import logging

from config import Config
from models import User



accounts_bp = Blueprint('accounts', __name__, template_folder='templates')
logger = logging.getLogger('logger')


@accounts_bp.route('/account')
@login_required
def account():

    user_posts = Sym_Encryption.decrypt_all_posts(current_user.posts)


    if current_user:
        return render_template("accounts/account.html", posts = user_posts, user = current_user)

@accounts_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@accounts_bp.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    #session authentication limit


    if current_user.is_authenticated:
        flash("You are already logged in.", category='info')
        return redirect(url_for('posts.posts'))

    ##if no attempts in session (new session)
    if session.get('attempts') is None:
        #clear falshed messages
        session['attempts'] = 0

    
    #if session attempts exceeded
    if session['attempts'] > Config.MAX_LOGIN_ATTEMPTS:
        reset_link = url_for('accounts.unlock')
        message = Markup(f'You have exceeded the maximum login attempts. <a href="{reset_link}">Click here to reset your attempts</a>.')
        flash(message, category='danger')
        logger.warning(f"[User:{form.email.data}, Attempts:{session['attempts']}, IP:{request.remote_addr}] Maximum login attempts reached.")
        return render_template('accounts/login.html')



    # On submit login form.
    if form.validate_on_submit():
        #user not real
        if not User.check_user_is_real(form.email.data):
            rem = handle_invalid_login_session(form.email.data)
            flash(f'Cannot find user email. {rem} attemp(s) remaining.', category='warning')
            return render_template('accounts/login.html', form = form)

        #password does not match
        if not User.verify_password_against_email(form.email.data, form.password.data):
            rem = handle_invalid_login_session(form.email.data)
            flash(f'Incorrect password. {rem} attemp(s) remaining.', category='warning')
            return render_template('accounts/login.html', form = form)


        user = User.find_user_from_email(form.email.data)
        pin_correct = user.verify_mfa_pin(input_pin = form.mfa_pin.data)
        mfa_enabled = user.verify_mfa_enabled()

        ##correct login+2fa
        if pin_correct:
            #reset attempts
            session.pop('attempts', None)
            #if MFa not enabled, set to true of successful login.
            if not user.verify_mfa_enabled():
                user.update_mfa(True)

            login_user(user)
            flash(f'Logged in.', category='success')
            
            #Generate log
            user.generate_log()

            #Check user privilegedes
            if current_user.role == 'db_admin':
                return redirect('http://127.0.0.1:5000/admin')
            elif current_user.role == 'sec_admin':
                return redirect(url_for('security.security'))
        
            return redirect(url_for('posts.posts'))
        ##
        ##
        ##Incorrect login attempt        

        #Incorrect pin entered and MFa not setup
        if not mfa_enabled and not pin_correct:
            flash('You have not enabled Multi-Factor Authentication. Please enable first to login.', category='error')
            qrURI = str(pyotp.totp.TOTP(user.mfa_key).provisioning_uri(form.email.data, 'CSC2035 BLOG'))
            return render_template('accounts/setup_mfa.html', secret=user.mfa_key, URI = qrURI)

        #if mfa setup and pin incorrect
        if mfa_enabled and not pin_correct: #pin correct check redundant but added for readability
            flash(f'Incorrect pin entered. {rem} attemp(s) remaining.', category='warning')
            return render_template('accounts/login.html', form = form)

    
    return render_template('accounts/login.html', form = form)

@accounts_bp.route('/unlock')
def unlock():
    session.pop('attempts', None)
    if '_flashes' in session:
        session['_flashes'].clear() #removed flashed messages
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
        if User.check_user_is_real(form.email.data):
            flash('Email already exists. ', category="danger")
            return render_template('accounts/registration.html', form=form)

        #create and commite new users
        new_user = User.create_user(form.email.data, form.firstname.data, form.lastname.data, form.phone.data, form.password.data)
        
        if new_user:
            flash('Account Created. You must set up Multi-Factor Authentication to login.', category='success')
            qrURI = str(pyotp.totp.TOTP(new_user.mfa_key).provisioning_uri(form.email.data, 'CSC2035 BLOG'))
            return render_template('accounts/setup_mfa.html', secret=new_user.mfa_key, URI = qrURI)

    return render_template('accounts/registration.html', form=form)



def handle_invalid_login_session(email):
    session['attempts'] += 1
    logger.warning(f"[User:{email}, Attempts:{session['attempts']}, IP:{request.remote_addr}] Invalid login.")
    return (Config.MAX_LOGIN_ATTEMPTS - session['attempts'])