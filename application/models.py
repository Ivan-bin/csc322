from application import db, login_manager, app
import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    interest = db.Column(db.Integer,nullable=False)
    credentials = db.Column(db.String(20), nullable=False)
    reference = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_pending = db.Column(db.Boolean, default=True, nullable=False)
    appeal = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"User('{self.name}', {self.last_name}', '{self.email}', '{self.reference}')"

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    rating = db.Column(db.Integer,nullable=False,default=0)
    compliments = db.relationship('Compliment', backref='recipient', lazy=True)
    complaints = db.relationship('Complaint', backref='complainee', lazy=True)
    UserBlacklist = db.relationship('UserBlacklist', backref='user_blacklisted', lazy=True)
    applications = db.relationship('Application', backref='referee', lazy=True)
    is_vip = db.Column(db.Boolean, default=False, nullable=False)
    is_su = db.Column(db.Boolean, default=False, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)

    def get_reset_token(self,expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100),unique=True, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable =False, default=0)
    def __repr__(self):
        return f"Project('{self.title}', '{self.date_created}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    content = db.Column(db.Text, nullable=False)
    group_id = db.Column(db.Integer,db.ForeignKey('project.id'),nullable=False)
    author = db.Column(db.String(100),db.ForeignKey('user.username'),nullable=False)
    def __repr__(self):
        return f"Post('{self.content}', '{self.author}')"

class Message1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    from_user = db.Column(db.String(100),nullable =False)
    to_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mess_type = db.Column(db.String(10),nullable=False)

    def __repr__(self):
        return f"Message('{self.title}', '{self.content}')"

class ProjectMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    project = db.Column(db.String(100), db.ForeignKey('project.title'),nullable=False)
    def __repr__(self):
        return f"Member('{self.project}', '{self.member}')"

class ApplicationBlacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    date_blacklisted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())

    def __repr__(self):
        return f"ApplicationBlacklisted('{self.application_id}')"

class Compliment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer,nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_pending = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"Compliment('{self.title}', '{self.date_posted}')"

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,default=datetime.datetime.now())
    content = db.Column(db.Text, nullable=False)
    complainant_id = db.Column(db.Integer,nullable=False)
    complainee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_pending = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"Complaint('{self.title}', '{self.date_posted}')"

class UserBlacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False,default=datetime.datetime.now())
    user_blacklisted_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"UserBlacklist('{self.user_blacklisted_id}', '{self.date_posted}')"

class Taboo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Taboo Word %r>' % self.id

class Blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    black = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    def __repr__(self):
        return f"Blacklist('{self.user}', '{self.black}')"

class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    white = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    def __repr__(self):
        return f"Whitelist('{self.user}', '{self.white}')"

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), db.ForeignKey('user.username'),nullable=False)
    date_posted =db.Column(db.DateTime,nullable=False,default=datetime.datetime.now())
    group = db.Column(db.String(100), db.ForeignKey('project.title'),nullable=False)
    def __repr__(self):
        return f"Meeting('{self.id}','{self.sender}', '{self.date_posted}')"

class Praisewarn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), db.ForeignKey('user.username'),nullable=False)
    to_user = db.Column(db.String(100), db.ForeignKey('user.username'),nullable=False)
    reason = db.Column(db.Text, nullable=False)
    date_posted =db.Column(db.DateTime,nullable=False,default=datetime.datetime.now())
    _type = db.Column(db.String(100), nullable=False)
    group = db.Column(db.String(100), db.ForeignKey('project.title'),nullable=False)
    def __repr__(self):
        return f"PraiseWarn('{self.sender}','{self._type}','{self.receiver}')"

class MeetingResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), db.ForeignKey('user.username'),nullable=False)
    result = db.Column(db.Integer,nullable=False)
    meeting_id = db.Column(db.Integer,db.ForeignKey('meeting.id'),nullable=False)
    def __repr__(self):
        return f"Result('{self.user}', '{self.result}', '{self.meeting_id}')"

class PraisewarnResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), db.ForeignKey('user.username'),nullable=False)
    result = db.Column(db.Integer,nullable=False)
    praisewarn_id = db.Column(db.Integer,db.ForeignKey(Praisewarn.id),nullable=False)
    def __repr__(self):
        return f"Result('{self.user}', '{self.result}', '{self.praisewarn_id}')"

class WarningList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), db.ForeignKey('user.username'),nullable=False)
    group = db.Column(db.String(100), db.ForeignKey('project.title'),nullable=False)

class Kick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), db.ForeignKey('user.username'),nullable=False)
    to_user = db.Column(db.String(100), db.ForeignKey('user.username'),nullable=False)
    reason = db.Column(db.Text, nullable=False)
    date_posted =db.Column(db.DateTime,nullable=False,default=datetime.datetime.now())
    group = db.Column(db.String(100), db.ForeignKey('project.title'),nullable=False)
    def __repr__(self):
        return f"Meeting('{self.id}','{self.sender}', '{self.date_posted}')"

class KickResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), db.ForeignKey('user.username'),nullable=False)
    result = db.Column(db.Integer,nullable=False)
    kick_id = db.Column(db.Integer,db.ForeignKey(Kick.id),nullable=False)
    def __repr__(self):
        return f"KickResult('{self.id}','{self.user}', '{self.result}')"

class Close(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), db.ForeignKey('user.username'),nullable=False)
    reason = db.Column(db.Text, nullable=False)
    date_posted =db.Column(db.DateTime,nullable=False,default=datetime.datetime.now())
    group = db.Column(db.String(100), db.ForeignKey('project.title'),nullable=False)
    def __repr__(self):
        return f"Meeting('{self.id}','{self.sender}', '{self.date_posted}')"

class CloseResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), db.ForeignKey('user.username'),nullable=False)
    result = db.Column(db.Integer,nullable=False)
    close_id = db.Column(db.Integer,db.ForeignKey(Close.id),nullable=False)
    def __repr__(self):
        return f"KickResult('{self.id}','{self.user}', '{self.result}')"