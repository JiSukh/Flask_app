from flask import Blueprint, render_template, flash, redirect, url_for
from accounts.forms import RegistrationForm, LoginForm
import config
import re



accounts_bp = Blueprint('accounts', __name__, template_folder='templates')


@accounts_bp.route('/account')
def account():
    return render_template("accounts/account.html")

@accounts_bp.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        user = config.User.query.filter_by(email=form.email.data).first()

        # If user exists, verify the password
        if user and user.verify_password(input_password=form.password.data):
            flash('Logged in.', category='success')
            return redirect(url_for('posts.posts'))

        else:
            flash('Account does not exists or you have entered the wrong password.', category='warning')
        

    return render_template('accounts/login.html', form = form)


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