from application import db, login_manager, app
from datetime import datetime
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
    posts = db.relationship('Post', backref='author', lazy=True)
    project = db.relationship('Project', backref='member', lazy=True)
    applications = db.relationship('Application', backref='referee', lazy=True)
    is_su = db.Column(db.Boolean, default=False, nullable=False)

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


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    members = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable =False, default=0)
    def __repr__(self):
        return f"Project('{self.title}', '{self.date_created}')"


class ApplicationBlacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    date_blacklisted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"ApplicationBlacklisted('{self.application_id}')"

# class BlackBox(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content=db.Column(db.String(200), nullable=False)
#     date_added=db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return f"BlackBox('{self.content}', '{self.date_added}')"

# class WhiteBox(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content=db.Column(db.String(200), nullable=False)
#     date_included=db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return f"WhiteBox('{self.content}', '{self.date_included}')"

# class TabooWords(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content=db.Column(db.String(200), nullable=False)
#     date_used=db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return f"TabooWords('{self.content}', '{self.date_used}')"