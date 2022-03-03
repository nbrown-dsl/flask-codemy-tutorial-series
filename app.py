from flask import Flask,render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
import os
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, template_folder="templates")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friends.db'
#initialize database
db = SQLAlchemy(app)


#create model class that can be mapped to database
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    people = db.relationship('Friend', backref='group', lazy=True)
    filename = db.Column(db.String(200),nullable=True)

    #create function to return string when we add something
    def __repr__(self):
        return '<Name %r>' % self.id

class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'),
        nullable=True)
    
    classes = db.relationship('ClassForm',
                    secondary='rolls')
    #create function to return string when we create new instance
    def __repr__(self):
        return '<Name %r>' % self.id

class ClassForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    subject = db.Column(db.String(200),nullable=False)
    teacher = db.Column(db.String(200),nullable=False)    
    friends = db.relationship('Friend',
                    secondary='rolls')

    #create function to return string when we create new instance
    def __repr__(self):
        return '<Name %r>' % self.id

# helper table to create many to many relationship between friend and classform
class Roll(db.Model):
    __tablename__ = 'rolls'
    id = db.Column(db.Integer, primary_key=True)
    classform_id = db.Column(db.Integer, db.ForeignKey('class_form.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('friend.id'))

    friend = relationship(Friend, backref=backref("rolls", cascade="all, delete-orphan"))
    classform = relationship(ClassForm, backref=backref("rolls", cascade="all, delete-orphan"))

db.create_all()
db.session.commit()

subscribers = []

@app.route('/delete/<int:id>/<modelName>')
def delete(id,modelName):
    if modelName == 'Friends':
        record_to_delete = Friend.query.get_or_404(id)
    if modelName == 'Groups':
        record_to_delete = Group.query.get_or_404(id)
    if modelName == 'ClassForm':
        record_to_delete = ClassForm.query.get_or_404(id)
        
    try:
        db.session.delete(record_to_delete)
        db.session.commit()
        return redirect(url_for('friends', modelName=modelName))
    except:
        return "there was a problem"


@app.route('/update/<int:id>/<modelName>', methods=["POST","GET"])
def update(id,modelName):
    groups = Group.query.order_by(Group.date_created)
    classes = ClassForm.query.order_by(ClassForm.subject)
    enrollment_ids = []

    if modelName == 'Friends':
        record_to_update = Friend.query.get_or_404(id)
        enrollments = Roll.query.filter_by(friend_id=id)        
        #create list of class ids that friend is enrolled on
        #when check boxes generated on web page each id is checked against this list
        #if on list then checkbox checked
        for enroll in enrollments:
            enrollment_ids.append(enroll.classform_id)
    if modelName == 'Groups':
        record_to_update = Group.query.get_or_404(id)
    if modelName == 'ClassForm':
        record_to_update = ClassForm.query.get_or_404(id)

    if request.method == "POST":
        record_to_update.name = request.form['name'] 
        if modelName == 'Friends':
            record_to_update.group_id = request.form['group'] 
            #delete previous enrollments
            enrollments = Roll.query.filter_by(friend_id=id)
            for enrollment in enrollments:
                db.session.delete(enrollment)
                db.session.commit()
            friend_classes = request.form.getlist("class")
            #iterates through list of checked checkboxes, adding to roll
            for friendClass in friend_classes:
                new_enrollment=Roll(friend_id=id, classform_id=friendClass)
                db.session.add(new_enrollment)
        if modelName == 'ClassForm':
            record_to_update.teacher = request.form['teacher']
            record_to_update.subject = request.form['subject']
        if modelName == 'Groups':
            record_to_update.filename = saveFile(request)
        
        try:
            db.session.commit()
            return redirect(url_for('friends', modelName=modelName))
        except Exception as e:
            return "problem updating"+str(e)
    else:
        return render_template('update.html', friend_to_update=record_to_update,modelName=modelName, groups = groups, classes = classes, enrollments=enrollment_ids)

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/about')
def about():
    
    names = ["Mr Brown","Turing","Gates"]
    return render_template('about.html',names=names)

@app.route('/friends/<modelName>' , methods=["POST","GET"])
def friends(modelName):
    
    title = modelName
    if modelName == "Friends":
        if request.method == "POST":
            friend_name = request.form['name']
            friend_group = request.form['group']
            new_friend = Friend(name=friend_name, group_id=friend_group)
            #push to database
            try:
                db.session.add(new_friend)
                db.session.commit()

                friend_classes = request.form.getlist('class')
                #iterates through list of checked checkboxes, adding to roll
                for friendClass in friend_classes:
                    new_enrollment=Roll(friend_id=new_friend.id, classform_id=friendClass)
                    db.session.add(new_enrollment)
                    db.session.commit()
            except:
                return "there was error adding your friend"
           
    #if group add
    elif modelName == "Groups":
        if request.method == "POST":
            group_name = request.form['name']
            filename = saveFile(request)
            new_group = Group(name=group_name, filename=filename)
                #push to databse
            try:
                db.session.add(new_group)
                db.session.commit()
            except Exception as e:    
                return print(e) 

    #if class add
    elif modelName == "ClassForm":
        if request.method == "POST":
            class_name = request.form['name']
            class_subject = request.form['subject']
            class_teacher = request.form['teacher']
            new_class = ClassForm(name=class_name, subject=class_subject, teacher=class_teacher)
            #push to databse
            try:
                db.session.add(new_class)
                db.session.commit()
            except:
                return "there was error adding the class"

    else:
        print("modelname not known") 

    friends = Friend.query.order_by(Friend.date_created)
    groups = Group.query.order_by(Group.date_created)
    classes = ClassForm.query.order_by(ClassForm.subject)
    return render_template('friends.html',title=title, friends = friends, groups = groups, classes = classes, modelName = modelName)

@app.route('/subscribe')
def subscribe():
    
    return render_template('subscribe.html')

@app.route('/form', methods=["POST"])
def form():
    
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    #from tutorial #6 - skip this as challenges with password security and authentication
    # message = "You have subscribed to my email newsletter"
    # server = smtplib.smtp("smtp.gmail.com", 587)
    # server.starttls()
    # server.login("nbrown@dwightlondon.org",os.getenv("GMPASSWORD"))
    # server.sendmail("nbrown@dwightlondon.org",email,message)

    if not first_name or not last_name or not email:
        error_statement = "all fields required"
        return render_template("subscribe.html",
        error_statement = error_statement,
        first_name = first_name,
        last_name = last_name,
        email = email)
        
    subscribers.append(f"{first_name} {last_name} | {email}")
    
    return render_template('form.html', subscribers = subscribers)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

def saveFile(request):
    if 'file' not in request.files:
        # flash('No file part')
        filename  = ""
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        # flash('No selected file')
        filename  = ""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename