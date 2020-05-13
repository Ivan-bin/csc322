import os
import secrets
from PIL import Image
import datetime
from flask import render_template, url_for, flash, redirect, request, abort
from application import app, db, bcrypt, mail
from application.forms import RegistrationForm, LoginForm, UpdateAccountForm, FormGroupForm,PraiseWarningForm,CloseForm,CloseAnswerForm\
    ,PostForm, ResetPasswordForm,MeetingForm, KickForm,CloseForm, InviteForm, KickAnswerForm,PWAnswerForm,RegistrationForm1
from application.models import User, Post, Project, Message1, ProjectMember, Praisewarn,Kick,KickResult ,Close,CloseResult,\
    Whitelist, Blacklist,Application,ApplicationBlacklist, Meeting,MeetingResult, Taboo,PraisewarnResult, WarningList, UserBlacklist,Complaint,Compliment
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

choices= ['08:00AM to 09:00AM','09:00AM to 10:00AM','10:00AM to 11:00AM','11:00AM to 12:00PM','12:00AM to 01:00PM',
    '01:00PM to 02:00PM','02:00PM to 03:00PM','03:00PM to 04:00PM','04:00PM to 05:00PM','05:00PM to 06:00PM'
    ,'06:00PM to 07:00PM','07:00PM to 08:00PM']

@app.route("/")
@app.route("/home")
def home():
    if User.query.filter(User.email=='superuser@csc322.edu').first():
        pass
    else:
        hashed_password = bcrypt.generate_password_hash('super').decode('utf-8')
        user = User(username='superuser',email='superuser@csc322.edu',password=hashed_password,is_su=True)
        db.session.add(user)
        db.session.commit()
    users = User.query.filter(User.email!='superuser@csc322.edu').order_by(User.rating.desc()).limit(3).all()
    projects = Project.query.order_by(Project.rating.desc()).limit(3).all()
    return render_template('home.html', users=users,projects=projects)

@app.route("/projects_and_users")
def projects_and_users():
    page = request.args.get('page',1,type=int)
    users = User.query.filter(User.email!='superuser@csc322.edu').order_by(User.id.asc()).paginate(page=page, per_page=5)
    projects = Project.query.order_by(Project.id.asc()).paginate(page=page, per_page=5)
    return render_template('projects_and_users.html', users=users,projects=projects)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/su")
def su():
    return render_template('su.html', title='SuperUser')

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
        flash('Your application has been sent.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
@app.route("/register1", methods=['GET', 'POST'])
def register1():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm1()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register1.html', title='Register', form=form)


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

@app.route("/post/<string:group_title>/new", methods=['GET', 'POST'])
@login_required
def new_post(group_title):
    form = PostForm()
    group = Project.query.filter(Project.title==group_title).first_or_404()
    print('fdfsdds')
    if form.validate_on_submit():
        print('12312')
        message = checkMessage(form.content.data.split())
        post = Post(content=message,group_id=group.id,author=current_user.username,date_posted=datetime.datetime.now())
        db.session.add(post)
        db.session.commit()
        flash('Your post has been posted','success')
        return redirect(url_for('grouppage',group_title=group.title))
    return render_template('create_post.html', title='New Post', form =form,legend ='New Post',group=group)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/form_group", methods=['GET', 'POST'])
@login_required
def form_group():
    users = User.query.filter(User.id!=current_user.id).all()
    superuser = User.query.filter_by(email='superuser@csc322.edu').first()
    users.remove(superuser)
    form = FormGroupForm()
    if form.validate_on_submit():
        members = request.form.getlist('members')
        if members == []:
            flash('Must select at least one member','danger')
            return redirect(url_for('form_group'))
        message = checkMessage(form.content.data.split())
        project = Project(title=form.title.data,description=message)
        db.session.add(project)
        db.session.commit()
        for member in members:
            b_user = User.query.filter_by(id=member).first()
            in_blacklist =Blacklist.query.filter((Blacklist.user==b_user.username) & (Blacklist.black==current_user.username)).first()
            in_whitelist =Whitelist.query.filter((Whitelist.user==b_user.username) & (Whitelist.white==current_user.username)).first()
            if in_blacklist is None:
                if in_whitelist is not None:
                    projmember = ProjectMember(project=form.title.data,member=member)
                    db.session.add(projmember)
                    db.session.commit()
                    flash('you are in '+b_user.username +'\'s white list','success')
                else:
                    message = Message1(title=form.title.data,content=checkMessage(form.content.data.split()),from_user=current_user.username,to_user=member,mess_type='invite')
                    db.session.add(message)
                    db.session.commit()
                    flash('Invite has been sent to ' +b_user.username,'success')
            else:
                flash('you got blocked by '+b_user.username,'warning')
        projmember2 = ProjectMember(project=form.title.data,member=current_user.id)
        db.session.add(projmember2)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('form_group.html',form =form,users=users)

@app.route("/message", methods=['GET', 'POST'])
@login_required
def message():
    message = Message1.query.filter(Message1.to_user == current_user.id).paginate(per_page=1)
    return render_template('message.html', posts=message)

@app.route("/application_list")
@login_required
def applications():
    if current_user.is_su:
        applications = Application.query.filter_by(is_pending=True).all()
        if applications:
            return render_template('application_list.html', applications=applications)
        else:
            flash('No more applications.', 'info')
            return render_template('application_list.html', applications=applications)

@app.route("/application_list/<int:application_id>")
def application(application_id):
    if current_user.is_su:
        application = Application.query.get_or_404(application_id)
        return render_template('application.html', title=application.email, application=application)

@app.route("/application_list/<int:application_id>/approve", methods=['POST'])
@login_required
def approve_application(application_id):
    if current_user.is_su:
        application = Application.query.get_or_404(application_id)
        user = User(username=application.email, email=application.email, password="$2b$12$xRMPe9Z7xLW6f83Ddv4pBeUCnnd8SV8IZvtmX7FwFHsbFd3fQf6Ke")
        db.session.add(user)
        application.is_pending = False
        db.session.commit()
        user2 = User.query.filter_by(email=user.email).first()
        send_approvedApplication_email(user2)
        flash('The application has been approved.','success')
        return redirect(url_for('applications'))

@app.route("/application_list/<int:application_id>/reject", methods=['POST'])
@login_required
def reject_application(application_id):
    if current_user.is_su:
        application = Application.query.get_or_404(application_id)
        user = ApplicationBlacklist(application_id=application_id)
        db.session.add(user)
        application.is_pending = False
        db.session.commit()
        msg = Message('Your Application was Rejected',
                  sender='noreply@demo.com',
                  recipients=[application.email])
        msg.body = f'''Dear
    {application.name}
        Your Application has been reviewed and has been rejectedd. 
        Active Teaming System.
        '''
        mail.send(msg)

        flash('The application has been rejected.','success')
        return redirect(url_for('applications'))

def send_approvedApplication_email(user):
    token = user.get_reset_token()
    msg = Message('Your Application was Approved',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''Congratulations! Your Application has been reviewed and has been approved. To set your new password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
Welcome to Active Teaming System.
'''
    mail.send(msg)

@app.route("/compliment_list")
@login_required
def compliments():
    if current_user.is_su:
        compliments = Compliment.query.filter_by(is_pending=True).all()
        if compliments:
            return render_template('compliment_list.html', compliments=compliments)
        else:
            flash('No more compliments.', 'info')
            return render_template('compliment_list.html', compliments=compliments)

@app.route("/compliment_list/<int:compliment_id>")
def compliment(compliment_id):
    if current_user.is_su:
        compliment = Compliment.query.get_or_404(compliment_id)
        sender = User.query.filter_by(id=compliment.sender_id).first()
        return render_template('compliment.html', title=compliment.recipient.email, compliment=compliment, sender=sender)

@app.route("/compliment_list/<int:compliment_id>/approve", methods=['POST'])
@login_required
def approve_compliment(compliment_id):
    if current_user.is_su:
        user_compliment = Compliment.query.get_or_404(compliment_id)
        user_compliment.is_pending = False
        user_compliment.recipient.rating += 1
        db.session.commit()
        msg = Message('New Complement',
                    sender='noreply@demo.com',
                    recipients=[user_compliment.recipient.email])
        msg.body = f'''Congratulations!
    {user_compliment.recipient.username}
    You have received a new compliment.
    """
    {user_compliment.content}
    """
    Your rating will increase 1 point.
    Active Teaming System.
    '''
        mail.send(msg)
        flash('Compliment has been sent.','success')
        return redirect(url_for('compliments'))

@app.route("/compliment_list/<int:compliment_id>/reject", methods=['POST'])
@login_required
def reject_compliment(compliment_id):
    if current_user.is_su:
        user_compliment = Compliment.query.get_or_404(compliment_id)
        user_compliment.is_pending = False
        db.session.commit()
        flash('The compliment has been rejected.','info')
        return redirect(url_for('compliments'))

@app.route("/complaint_list")
@login_required
def complaints():
    if current_user.is_su:
        complaints = Complaint.query.filter_by(is_pending=True).all()
        if complaints:
            return render_template('complaint_list.html', complaints=complaints)
        else:
            flash('No more complaints.', 'info')
            return render_template('complaint_list.html', complaints=complaints)

@app.route("/complaint_list/<int:complaint_id>")
def complaint(complaint_id):
    if current_user.is_su:
        complaint = Complaint.query.get_or_404(complaint_id)
        complainant = User.query.filter_by(id=complaint.complainant_id).first()
        return render_template('complaint.html', title=complaint.complainee.email, complaint=complaint, complainant=complainant)

@app.route("/complaint_list/<int:complaint_id>/approve", methods=['POST'])
@login_required
def approve_complaint(complaint_id):
    if current_user.is_su:
        user_complaint = Complaint.query.get_or_404(complaint_id)
        user_complaint.is_pending = False
        user_complaint.complainee.rating -= 1
        db.session.commit()
        msg = Message('New Complaint',
                    sender='noreply@demo.com',
                    recipients=[user_complaint.complainee.email])
        msg.body = f'''Warning!
    {user_complaint.complainee.username}
    You have received a new complaint:
    """
    {user_complaint.content}
    """
    Your rating will decrease 1 point.
    Active Teaming System.
    '''
        mail.send(msg)
        flash('Complaint has been sent.','success')
        return redirect(url_for('complaints'))
        
@app.route("/complaint_list/<int:complaint_id>/reject", methods=['POST'])
@login_required
def reject_complaint(complaint_id):
    if current_user.is_su:
        user_complaint = complaint.query.get_or_404(complaint_id)
        user_complaint.is_pending = False
        db.session.commit()
        flash('The complaint has been rejected.','info')
        return redirect(url_for('complaints'))

@app.route("/complaint_list/<int:complaint_id>/blacklist_user", methods=['POST'])
@login_required
def blacklist_user_complaint(complaint_id):
    if current_user.is_su:
        user_complaint = Complaint.query.get_or_404(complaint_id)
        user_complaint.is_pending = False
        user = UserBlacklist(user_blacklisted_id=user_complaint.complainee.id)
        db.session.add(user)
        db.session.commit()
        flash('The user has been blacklisted.','info')
        return redirect(url_for('complaints'))

@app.route('/user_blacklist', methods=['POST', 'GET'])
@login_required
def user_blacklist():
    if current_user.is_su:
        if request.method == 'POST':
            user_email = request.form['content']
            user = User.query.filter_by(email=user_email).first()
            if user:
                new_user = UserBlacklist(user_blacklisted_id=user.id)
                try:
                    user.is_blacklisted = True
                    db.session.add(new_user)
                    db.session.commit()
                    return redirect('user_blacklist')
                except:
                    return 'There was an issue adding your word'
            else:
                flash('No user with that email.','info')
                return redirect('user_blacklist')
        else:
            users = UserBlacklist.query.order_by(UserBlacklist.id).all()
            return render_template('user_blacklist.html', users=users)

@app.route('/remove_blacklisted_user/<int:id>',methods=['POST', 'GET'])
@login_required
def remove_blacklisted_user(id):
    if current_user.is_su:
        user_to_remove = UserBlacklist.query.get_or_404(id)
        try:
            user_to_remove.user_blacklisted.is_blacklisted = False
            db.session.delete(user_to_remove)
            db.session.commit()
            flash('Remove','success')
            return redirect(url_for('user_blacklist'))
        except:
            return 'There was a problem deleting that task'

@app.route('/taboo', methods=['POST', 'GET'])
@login_required
def taboo():
    if current_user.is_su:
        if request.method == 'POST':
            word_content = request.form['content']
            new_word = Taboo(word=word_content)
            try:
                db.session.add(new_word)
                db.session.commit()
                return redirect('taboo')
            except:
                return 'There was an issue adding your word'
        else:
            words = Taboo.query.order_by(Taboo.id).all()
            return render_template('taboo.html', words=words)

@app.route('/deleteword/<int:id>',methods=['POST', 'GET'])
def deleteword(id):
    if current_user.is_su:
        word_to_delete = Taboo.query.get_or_404(id)
        try:
            db.session.delete(word_to_delete)
            db.session.commit()
            flash('Remove','success')
            return redirect(url_for('taboo'))
        except:
            return 'There was a problem deleting that task'

@app.route("/message/<int:message_id>/accept", methods=['POST'])
@login_required
def accept_message(message_id):
    message = Message1.query.get_or_404(message_id)
    project = message.title
    user = message.to_user
    member = ProjectMember(project=project,member=user)
    db.session.add(member)
    db.session.commit()
    db.session.delete(message)
    db.session.commit()
    if request.form.get('whitelist') is not None:
        b_user = User.query.filter_by(id=message.from_user).first()
        white = Whitelist(user=current_user.username,white=message.from_user)
        db.session.add(white)
        db.session.commit()
    flash('You have successfully accepted the invite, the group link is under Account - Groups','success')
    return redirect(url_for('message'))

@app.route("/message/<int:message_id>/decline", methods=['POST'])
@login_required
def decline_message(message_id):
    message = Message1.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    if request.form.get('blacklist') is not None:
        black = Blacklist(user=current_user.username,black=message.from_user)
        db.session.add(black)
        db.session.commit()
    flash('you have successfully decline the invite','success')
    return redirect(url_for('message'))

@app.route("/delete/<int:message_id>", methods=['POST','GET'])
@login_required
def remove_message(message_id):
    message = Message1.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('you have successfully remove the message','success')
    return redirect(url_for('message'))

@app.route("/blackwhite-list", methods=['GET', 'POST'])
@login_required
def black_white():
    white = Whitelist.query.filter(Whitelist.user==current_user.username).all()
    black = Blacklist.query.filter(Blacklist.user==current_user.username).all()
    return render_template('black_white.html',whitelist=white,blacklist=black)

@app.route("/white_delete/<int:list_id>", methods=['GET', 'POST'])
@login_required
def delete_white(list_id):
    delete = Whitelist.query.get_or_404(list_id)
    try:
        db.session.delete(delete)
        db.session.commit()
        flash('User had been remove','success')
        return redirect(url_for('black_white'))
    except:
        flash('There was a problem deleting that task','warning')
        return redirect(url_for('black_white'))

@app.route("/black_delete/<int:list_id>", methods=['GET', 'POST'])
@login_required
def delete_black(list_id):
    delete = Blacklist.query.get_or_404(list_id)
    try:
        db.session.delete(delete)
        db.session.commit()
        flash('User had been remove','success')
        return redirect(url_for('black_white'))
    except:
        flash('There was a problem deleting that task','warning')
        return redirect(url_for('black_white'))
        
@app.route("/grouppage/<string:group_title>", methods=['GET', 'POST'])
def grouppage(group_title):
    group = Project.query.filter(Project.title==group_title).first_or_404()
    warninglist = WarningList.query.filter((WarningList.group==group.title) & (WarningList.user==current_user.username)).all()
    if len(warninglist)>=3:
        kick_user = User.query.filter(User.id==current_user.id).first()
        kick_user.rating-=10
        db.session.add(kick_user)
        db.session.commit()
        kick = ProjectMember.query.filter((ProjectMember.project==group.title)&(ProjectMember.member==current_user.id)).first()
        db.session.delete(kick)
        db.session.commit()
        flash('Sorry you got kick from the group','danger')
        return redirect(url_for('group'))
    getid = ProjectMember.query.filter(ProjectMember.project==group.title).all()
    meeting = Meeting.query.filter_by(group=group.title).first()
    kick = Kick.query.filter_by(group=group.title).first()
    praisewarn = Praisewarn.query.filter_by(group=group.title).first()
    close = Close.query.filter_by(group=group.title).first()
    users = []
    for uid in getid:
        users += User.query.filter(User.id == uid.member).all()
    result = []
    if meeting is None:
        pass
    else:
        meet = MeetingResult.query.filter_by(meeting_id=meeting.id).all()
        time = datetime.datetime.now()- meeting.date_posted
        for m in meet:
            if current_user.username == m.user:
                meeting = []
                break
        if time.seconds >= 300 or len(meet)==len(users):
            meeting1 = Meeting.query.filter_by(group=group.title).first()
            db.session.delete(meeting1)
            db.session.commit()
            for m in meet:
                result.append(m.result)
                db.session.delete(m)
                db.session.commit()
            for user in users:
                title = "Meeting Poll Result for Group "+ group.title
                content = choices[max(set(result), key = result.count)-1]
                from_user = meeting1.sender
                to_user = user.id
                mess = Message1(title=title,content=content,from_user=from_user,to_user=to_user,mess_type="meeting")
                db.session.add(mess)
                db.session.commit()
    if praisewarn is None:
        pass
    else:
        res=[]
        praisewarn1 = Praisewarn.query.filter_by(group=group.title).first()
        pwresult = PraisewarnResult.query.filter_by(praisewarn_id=praisewarn1.id).all()
        time = datetime.datetime.now()- praisewarn.date_posted
        for result in pwresult:
            if (current_user.username == praisewarn1.to_user):
                praisewarn = []
                break
            if (current_user.username == result.user):
                praisewarn = []
                break
        if time.seconds >= 300 or len(pwresult)==(len(users)-1):
            for r in pwresult:
                res.append(r.result)
                db.session.delete(r)
                db.session.commit()
            ans = max(set(res), key = res.count)
            for user in users:
                if user.username != praisewarn1.to_user:
                    title = "Praise/Warning Poll Result for Group "+ group.title
                    if ans == 0:
                        content = 'Fail to ' + praisewarn1._type + praisewarn1.to_user
                    else:
                        content = 'Success! ' + praisewarn1._type +' to '+ praisewarn1.to_user
                    from_user = praisewarn1.sender
                    to_user = user.id
                    mess = Message1(title=title,content=content,from_user=from_user,to_user=to_user,mess_type="meeting")
                    db.session.add(mess)
                    db.session.commit()
                else:
                    if ans == 0:
                        pass
                    else:
                        content = 'Group member(s) sent a ' + praisewarn1._type + ' to you'
                        title = "You Recieved a "+ praisewarn1._type +" from " +group.title
                        from_user = praisewarn1.sender
                        to_user = user.id
                        mess = Message1(title=title,content=content,from_user=from_user,to_user=to_user,mess_type="meeting")
                        db.session.add(mess)
                        db.session.commit()
                        warn = WarningList(user=praisewarn1.to_user,group=group.title)
                        db.session.add(warn)
                        db.session.commit()
            db.session.delete(praisewarn1)
            db.session.commit()
    if kick is None:
        pass
    else:
        res=[]
        kick1 = Kick.query.filter_by(group=group.title).first()
        kick_result = KickResult.query.filter_by(kick_id=kick1.id).all()
        time = datetime.datetime.now()- kick1.date_posted
        for result in kick_result:
            if (current_user.username == kick1.to_user):
                kick = []
                break
            if (current_user.username == result.user):
                kick = []
                break
        if time.seconds >= 300 or len(kick_result)==(len(users)-1):
            for r in kick_result:
                res.append(r.result)
                db.session.delete(r)
                db.session.commit()
            ans = max(set(res), key = res.count)
            for user in users:
                if user.username != kick1.to_user:
                    title = "Kicking Poll Result for Group "+ group.title
                    if ans == 0:
                        content = 'Fail to kick' + kick1.to_user
                    else:
                        content = 'Successfully kicked '+ kick1.to_user
                    from_user = kick1.sender
                    to_user = user.id
                    mess = Message1(title=title,content=content,from_user=from_user,to_user=to_user,mess_type="meeting")
                    db.session.add(mess)
                    db.session.commit()
                else:
                    if ans == 0:
                        pass
                    else:
                        content = 'Reason: ' + kick1.reason
                        title = 'You got kick from group ' + group.title
                        from_user = kick1.sender
                        to_user = user.id
                        mess = Message1(title=title,content=content,from_user=from_user,to_user=to_user,mess_type="meeting")
                        db.session.add(mess)
                        db.session.commit()
                        user = ProjectMember.query.filter((ProjectMember.member==user.id)&(ProjectMember.project==group.title)).first()
                        db.session.delete(user)
                        db.session.commit()
            db.session.delete(kick1)
            db.session.commit()
    if close is None:
        pass
    else:
        res=[]
        close1 = Close.query.filter_by(group=group.title).first()
        close_result = CloseResult.query.filter_by(close_id=close1.id).all()
        time = datetime.datetime.now()- close1.date_posted
        for result in close_result:
            if (current_user.username == result.user):
                close = []
                break
        if time.seconds >= 300 or len(close_result)==(len(users)):
            for r in close_result:
                res.append(r.result)
                db.session.delete(r)
                db.session.commit()
            ans = max(set(res), key = res.count)
            for user in users:
                    title = "Close Group Poll Result for "+ group.title
                    if ans == 0:
                        content = 'Fail' 
                    else:
                        content = 'Success'
                        close_g = ProjectMember.query.filter_by(member=user.id).first()
                        db.session.delete(close_g)
                        db.session.commit()
                    from_user = close1.sender
                    to_user = user.id
                    mess = Message1(title=title,content=content,from_user=from_user,to_user=to_user,mess_type="meeting")
                    db.session.add(mess)
                    db.session.commit()
            if ans == 1:
                grp = Project.query.filter(Project.title==group.title).first()
                db.session.delete(grp)
                db.session.commit()
            db.session.delete(close1)
            db.session.commit()
    meetingform = MeetingForm()
    if meetingform.validate_on_submit():
        meet = Meeting.query.filter_by(group=group.title).first()
        meetingresult = MeetingResult(user=current_user.username,result=meetingform.time.data,meeting_id=meet.id)
        db.session.add(meetingresult)
        db.session.commit()
        flash('Submitted1, result will send to your message box','success')
        return redirect(url_for('grouppage',group_title=group_title))
    pwform = PWAnswerForm()
    if pwform.validate_on_submit():
        praisewarn1 = Praisewarn.query.filter_by(group=group.title).first()
        praisewarningresult = PraisewarnResult(user=current_user.username,result=pwform.pw.data,praisewarn_id=praisewarn1.id)
        db.session.add(praisewarningresult)
        db.session.commit()
        flash('Submitted, result will send to your message box','success')
        return redirect(url_for('grouppage',group_title=group_title))
    kickform = KickAnswerForm()
    if kickform.validate_on_submit():
        kick = Kick.query.filter_by(group=group.title).first()
        kickresult = KickResult(user=current_user.username,result=kickform.kick.data,kick_id=kick.id)
        db.session.add(kickresult)
        db.session.commit()
        flash('Submitted, result will send to your message box','success')
        return redirect(url_for('grouppage',group_title=group_title))
    closeform = CloseAnswerForm()
    if closeform.validate_on_submit():
        close = Close.query.filter_by(group=group.title).first()
        closeresult = CloseResult(user=current_user.username,result=closeform.close.data,close_id=close.id)
        db.session.add(closeresult)
        db.session.commit()
        flash('Submitted, result will send to your message box','success')
        return redirect(url_for('grouppage',group_title=group_title))
    posts = Post.query.filter(Post.group_id==group.id).order_by(Post.date_posted.desc()).all()
    return render_template('grouppage.html',group=group,users=users,posts=posts,meetingform=meetingform,\
        kickform=kickform,meeting=meeting,praisewarn=praisewarn,kick=kick,pwform=pwform,closeform=closeform,close=close)

@app.route("/group", methods=['GET', 'POST'])
def group():
    groups = ProjectMember.query.filter(ProjectMember.member==current_user.id).all()
    return render_template('group.html', groups=groups)

@app.route("/praisewarning/<string:group_title>/", methods=['GET', 'POST'])
@login_required
def praise_warning(group_title):
    form = PraiseWarningForm()
    members = request.form.getlist('members')
    group = Project.query.filter(Project.title==group_title).first_or_404()
    getid = ProjectMember.query.filter(ProjectMember.project==group.title).all()
    users = []
    for uid in getid:
        if uid.member != current_user.id:
            users += User.query.filter(User.id == uid.member).all()
    if form.validate_on_submit():
        praisewarn = Praisewarn.query.filter(Praisewarn.group==group.title).first()
        if praisewarn is None:
            if members == [] or len(members)>1:
                flash('Select at most/least one member','danger')
                return redirect(url_for('praise_warning',group_title=group.title))
            if form.porw.data == '1':
                porw = 'praise'
            else:
                porw='warn'
            b_user = User.query.filter_by(id=members[0]).first()
            praiseorwarn = Praisewarn(sender=current_user.username,to_user=b_user.username,group=group.title,\
                    date_posted=datetime.datetime.now(),_type=porw,reason=form.reason.data)
            db.session.add(praiseorwarn)
            db.session.commit()
            praisewarn = Praisewarn.query.filter(Praisewarn.group==group.title).first()
            result = PraisewarnResult(user=current_user.username,result=1,praisewarn_id=praisewarn.id)
            db.session.add(result)
            db.session.commit()
            flash('Sent','success')
        else:
            time = datetime.datetime.now() - praisewarn.date_posted
            flash('One Praise/Warning Poll at a time new meeting poll available in '+ str(datetime.timedelta(seconds=300-time.seconds)),'warning')
        return redirect(url_for('grouppage',group_title=group.title))
    return render_template('praisewarning.html', title='PraiseWaring', form =form,legend ='Praise or Warn',group=group,users=users)

@app.route("/meeting/<string:group_title>/", methods=['GET', 'POST'])
@login_required
def meeting(group_title):
    form = MeetingForm()
    group = Project.query.filter(Project.title==group_title).first_or_404()
    getid = ProjectMember.query.filter(ProjectMember.project==group.title).all()
    if form.validate_on_submit():
        meet = Meeting.query.filter_by(group=group.title).first()
        if meet is None:
            meeting = Meeting(sender=current_user.username,date_posted=datetime.datetime.now(),group=group.title)
            db.session.add(meeting)
            db.session.commit()
            meet1 = Meeting.query.filter_by(sender=current_user.username).first()
            meetingresult = MeetingResult(user=current_user.username,result=form.time.data, meeting_id=meet1.id)
            db.session.add(meetingresult)
            db.session.commit()
            flash('Submitted, result will send to your message box','success')
        else:
            time = datetime.datetime.now() - meet.date_posted
            flash('One Meeting Poll at a time new meeting poll available in '+ str(datetime.timedelta(seconds=300-time.seconds)),'warning')
        return redirect(url_for('grouppage',group_title=group_title))
    return render_template('meeting.html', title='ScheduleMeeting', form =form,legend ='Schedule Meeting',group=group)

@app.route("/kick/<string:group_title>/", methods=['GET', 'POST'])
@login_required
def kick(group_title):
    form = KickForm()
    group = Project.query.filter(Project.title==group_title).first_or_404()
    getid = ProjectMember.query.filter(ProjectMember.project==group.title).all()
    members = request.form.getlist('members')
    users = []
    for uid in getid:
        if uid.member != current_user.id:
            users += User.query.filter(User.id == uid.member).all()
    if form.validate_on_submit():
        kick = Kick.query.filter(Kick.group==group.title).first()
        if kick is None:
            if members == [] or len(members)>1:
                flash('Select at most/least one member','danger')
                return redirect(url_for('praise_warning',group_title=group.title))
            b_user = User.query.filter_by(id=members[0]).first()
            kick_member = Kick(sender=current_user.username,to_user=b_user.username,group=group.title,\
                    date_posted=datetime.datetime.now(),reason=form.reason.data)
            db.session.add(kick_member)
            db.session.commit()
            kick = Kick.query.filter(Kick.group==group.title).first()
            result = KickResult(user=current_user.username,result=1,kick_id=kick.id)
            db.session.add(result)
            db.session.commit()
            flash('Sent','success')
            return redirect(url_for('grouppage',group_title=group_title))
        else:
            time = datetime.datetime.now() - kick.date_posted
            flash('One Praise/Warning Poll at a time new meeting poll available in '+ str(datetime.timedelta(seconds=300-time.seconds)),'warning')
    return render_template('kick.html', title='Kick', form =form,legend ='Kick',group=group,users=users)

@app.route("/close/<string:group_title>/", methods=['GET', 'POST'])
@login_required
def close(group_title):
    form = CloseForm()
    group = Project.query.filter(Project.title==group_title).first_or_404()
    getid = ProjectMember.query.filter(ProjectMember.project==group.title).all()
    users = []
    if form.validate_on_submit():
        close = Close.query.filter(Kick.group==group.title).first()
        if close is None:
            close_group = Close(sender=current_user.username,group=group.title,\
                    date_posted=datetime.datetime.now(),reason=form.reason.data)
            db.session.add(close_group)
            db.session.commit()
            close = Close.query.filter(Close.group==group.title).first()
            result = CloseResult(user=current_user.username,result=1,close_id=close.id)
            db.session.add(result)
            db.session.commit()
            flash('Sent','success')
            return redirect(url_for('grouppage',group_title=group_title))
        else:
            time = datetime.datetime.now() - close.date_posted
            flash('One Praise/Warning Poll at a time new meeting poll available in '+ str(datetime.timedelta(seconds=300-time.seconds)),'warning')
    return render_template('close.html', title='Close', form =form,legend ='Close Group',group=group)

@app.route("/invite/<string:group_title>/", methods=['GET', 'POST'])
@login_required
def invite(group_title):
    form = InviteForm()
    group = Project.query.filter(Project.title==group_title).first_or_404()
    getid = ProjectMember.query.filter(ProjectMember.project==group.title).all()
    user = User.query.filter(User.email!='superuser@csc322.edu').all()
    users = []
    count = 1
    for u in user:
        for uid in getid:
            if u.id == uid.member:
                count = 1
                break
            if count == len(getid):
                users += User.query.filter(User.id == u.id).all()
                count = 1
            count+=1
    if form.validate_on_submit():
        members = request.form.getlist('members')
        if members == []:
            flash('Must select at least one member','danger')
            return redirect(url_for('invite',group_title=group.title))
        for member in members:
            b_user = User.query.filter_by(id=member).first()
            in_blacklist =Blacklist.query.filter((Blacklist.user==b_user.username) & (Blacklist.black==current_user.username)).first()
            in_whitelist =Whitelist.query.filter((Whitelist.user==b_user.username) & (Whitelist.white==current_user.username)).first()
            if in_blacklist is None:
                if in_whitelist is not None:
                    projmember = ProjectMember(project=form.title.data,member=member)
                    db.session.add(projmember)
                    db.session.commit()
                    flash('you are in '+b_user.username +'\'s white list','success')
                else:
                    message = Message1(title=group.title,content=form.reason.data,from_user=current_user.username,to_user=member,mess_type="invite")
                    db.session.add(message)
                    db.session.commit()
                    flash('Invite has been sent to ' +b_user.username,'success')
            else:
                flash('you got blocked by '+b_user.username,'warning')
        return redirect(url_for('grouppage',group_title=group_title))
    return render_template('invite.html', title='Invite', form =form,legend ='Invite',group=group,users=users)

def checkMessage(message):
    mess = ''
    taboo = Taboo.query.all()
    count = 1
    for m in message:
        if taboo == []:
            mess+=m
            mess+=' '
        else:
            for t in taboo:
                if t.word == m:
                    mess+=m.replace(m,'*'*len(m))
                    mess+=' '
                    count = 1
                    break
                else:
                    if count == len(taboo):
                        mess+=m
                        mess+=' '
                    count+=1
            count = 1

    return mess