import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from application import app, db, bcrypt
from application.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ResetPasswordForm, RequestResetForm, FormGroupForm
from application.models import Application, ApplicationBlacklist, User, Post, Project
from flask_login import login_user, current_user, logout_user, login_required
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

API_KEY = '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'

@app.route("/")
@app.route("/home")
def home():
    users = User.query.order_by(User.rating.desc()).limit(3).all()
    projects = Project.query.order_by(Project.rating.desc()).limit(3).all()
    return render_template('home.html', users=users,projects=projects)

@app.route("/projects_and_users")
def projects_and_users():
    page = request.args.get('page',1,type=int)
    users = User.query.order_by(User.id.asc()).paginate(page=page, per_page=5)
    projects = Project.query.order_by(Project.id.asc()).paginate(page=page, per_page=5)
    return render_template('projects_and_users.html', users=users,projects=projects)

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Application.query.filter_by(email=form.email.data).first()
        if user:
            blacklisted_user = ApplicationBlacklist.query.filter_by(application_id=user.id).first()
            if blacklisted_user:
                flash('The email entered has been blacklisted')
                return redirect(url_for('login'))

            if user.is_pending:
                flash('Your application still under review, Please try again later')
                return redirect(url_for('login'))
       
        user2 = Application(name=form.name.data, last_name=form.lastName.data, email=form.email.data, interest=form.interest.data, credentials=form.credentials.data, reference=form.reference.data)
        db.session.add(user2) 
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('your post had been created','success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form =form,legend ='new post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html',title=post.title,post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('your post have been update','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form =form, legend ='update post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('your post have been delete','success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    message = Mail(
        from_email='noreply@demo.com',
        to_emails=user.email,
        subject='Password Reset Request',
        html_content= f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    )
    try:
        sg = SendGridAPIClient(API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/form_group", methods=['GET', 'POST'])
@login_required
def form_group():
    users = User.query.filter(User.id!=current_user.id).all()
    form = FormGroupForm()
    if form.validate_on_submit():
        print(request.form.getlist('members'))
        members = request.form.getlist('members')
        if members == []:
            flash('Must select at least one member','danger')
            return redirect(url_for('form_group'))
        flash('Invite(s) has been sent','success')
        return redirect(url_for('home'))
    return render_template('form_group.html',form =form,users=users)

@app.route("/message", methods=['GET', 'POST'])
@login_required
def message():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('message.html', posts=posts)

@app.route("/application_list")
def applications():
    applications = Application.query.filter_by(is_pending=True).all()
    if applications:
        return render_template('application_list.html', applications=applications)
    else:
        return redirect(url_for('home'))

@app.route("/application_list/<int:application_id>")
def application(application_id):
    application = Application.query.get_or_404(application_id)
    return render_template('application.html', title=application.email, application=application)