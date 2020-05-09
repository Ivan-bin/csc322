from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField,TextAreaField, BooleanField,ValidationError, SelectMultipleField, widgets, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired
from application.models import User

interestList = [('1', 'a'), ('2', 'b'), ('3', 'c'), ('4', 'd'), ('5', 'e'), ('6', 'f')]

class RegistrationForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    lastName = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    interest = SelectField('Interest', choices=interestList)
    credentials = StringField('Credentials',
                           validators=[DataRequired(), Length(min=2, max=50)])
    reference = IntegerField('Reference', validators=[InputRequired()])
    submit = SubmitField('Sign Up')
    

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Taken')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Updated profile pic',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Taken')
    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Taken')

class PostForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    content = TextAreaField('Content',validators=[DataRequired()])
    submit = SubmitField('Post')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('no account with that email')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')




class FormGroupForm(FlaskForm):
    title = StringField('Group Title',validators=[DataRequired()])
    content = TextAreaField('Message (optional)')
    submit = SubmitField('Send')