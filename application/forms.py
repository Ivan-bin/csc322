from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField,TextAreaField, BooleanField,ValidationError, SelectMultipleField, widgets, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired
from application.models import User

interestList = [('1', 'Frontend developer'), ('2', 'Backend expert'), ('3', 'Database expert'), ('4', 'AI expert'), ('5', 'Manager'), ('6', 'Full-Stack developer')]

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


class RegistrationForm1(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

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
    content = TextAreaField('Content',validators=[DataRequired()])
    submit = SubmitField('Post')

class FormGroupForm(FlaskForm):
    title = StringField('Group Title',validators=[DataRequired()])
    content = TextAreaField('Group Description',validators=[DataRequired()])
    submit = SubmitField('Send')

class PraiseWarningForm(FlaskForm):
    porw = SelectField('Select',choices=[('1','Prasie'),('2','Warning')], validators=[DataRequired()])
    reason = TextAreaField('Reason',validators=[DataRequired()])
    submit = SubmitField('Send')

class MeetingForm(FlaskForm):
    choices= [('1','08:00AM to 09:00AM'),('2','09:00AM to 10:00AM'),('3','10:00AM to 11:00AM'),('4','11:00AM to 12:00PM'),('5','12:00AM to 01:00PM'),
    ('6','01:00PM to 02:00PM'),('7','02:00PM to 03:00PM'),('8','03:00PM to 04:00PM'),('9','04:00PM to 05:00PM'),('10','05:00PM to 06:00PM')
    ,('11','06:00PM to 07:00PM'),('12','07:00PM to 08:00PM')]
    time= SelectField('Pick a time',choices=choices, validators=[DataRequired()])
    reason = TextAreaField('Meeting Reason (optional)')
    submit = SubmitField('Send')

class VoteSUForm(FlaskForm):
    vip = User.query.filter(User.is_vip==True).all()
    time= SelectField('Select',choices=[(v.id, v.username)for v in vip], validators=[DataRequired()])
    submit = SubmitField('Send')

class KickForm(FlaskForm):
    reason = TextAreaField('Reason',validators=[DataRequired()])
    submit = SubmitField('Send')

class KickAnswerForm(FlaskForm):
    kick= SelectField('Agree/Disagree',choices=[('1','Agree'),('0','Disagree')], validators=[DataRequired()])
    submit = SubmitField('Send')

class PWAnswerForm(FlaskForm):
    pw = SelectField('Agree/Disagree',choices=[('1','Agree'),('0','Disagree')], validators=[DataRequired()])
    submit = SubmitField('Send')

class CloseForm(FlaskForm):
    reason = TextAreaField('Reason',validators=[DataRequired()])
    submit = SubmitField('Send')

class CloseAnswerForm(FlaskForm):
    close = SelectField('Agree/Disagree',choices=[('1','Agree'),('0','Disagree')], validators=[DataRequired()])
    submit = SubmitField('Send')

class InviteForm(FlaskForm):
    reason = TextAreaField('Reason',validators=[DataRequired()])
    submit = SubmitField('Send')