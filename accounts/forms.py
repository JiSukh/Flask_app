from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp, Email



class RegistrationForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email(message= 'Invalid Email.')])
    firstname = StringField(validators=[DataRequired(), Regexp(regex = '^[A-Za-z-]+$', message= 'Name must only include English letters and/or hyphens (-)')])
    lastname = StringField(validators=[DataRequired(), Regexp(regex = '^[A-Za-z-]+$', message= 'Name must only include English letters and/or hyphens (-))')])
    phone = StringField(validators=[DataRequired(), Regexp(regex = '^(02\d-\d{8}|011\d-\d{7}|01\d{2,3}-\d{5,6})$', message='Invalid phone number')])
    password = PasswordField(validators=[DataRequired(), Length(min = 8, message = "Length of password must be longer than 8."), Regexp(regex ='^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)[a-zA-Z\d\W]', message = "Invalid password. Valid password must contain: \nAtleast one special character\nAtleast one uppercase character\nAtleast 8 characters in total")])
    confirm_password = PasswordField(validators=[DataRequired(), EqualTo('password', message="Both password fields must be the same.")])
    submit = SubmitField()

class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    mfa_pin = StringField(validators=[DataRequired()])
    #recaptcha = RecaptchaField()
    submit = SubmitField()