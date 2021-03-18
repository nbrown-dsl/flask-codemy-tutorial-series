from flask import Flask,render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# import smtplib

app = Flask(__name__, template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friends.db'
#initialize database
db = SQLAlchemy(app)

#create model class that can be mapped to database
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    people = db.relationship('Friend', backref='group', lazy=True)

    #create function to return string when we add something
    def __repr__(self):
        return '<Name %r>' % self.id

class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'),
        nullable=True)

    #create function to return string when we create new instance
    def __repr__(self):
        return '<Name %r>' % self.id



db.create_all()
db.session.commit()

subscribers = []

@app.route('/delete/<int:id>/<modelName>')
def delete(id,modelName):
    if modelName == 'Friends':
        record_to_delete = Friend.query.get_or_404(id)
    if modelName == 'Groups':
        record_to_delete = Group.query.get_or_404(id)
        
    try:
        db.session.delete(record_to_delete)
        db.session.commit()
        return redirect(url_for('friends', modelName=modelName))
    except:
        return "there was a problem"


@app.route('/update/<int:id>/<modelName>', methods=["POST","GET"])
def update(id,modelName):
    if modelName == 'Friends':
        record_to_update = Friend.query.get_or_404(id)
    if modelName == 'Groups':
        record_to_update = Group.query.get_or_404(id)
    if request.method == "POST":
        record_to_update.name = request.form['name'] 
        try:
            db.session.commit()
            return redirect(url_for('friends', modelName=modelName))
        except:
            return "problem updating"
    else:
        return render_template('update.html', friend_to_update=record_to_update,modelName=modelName)

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
                
            except:
                return "there was error adding your friend"
            
    #if group update
    elif modelName == "Groups":
        if request.method == "POST":
            group_name = request.form['name']
            new_group = Group(name=group_name)
            #push to databse
            try:
                db.session.add(new_group)
                db.session.commit()
            except:
                return "there was error adding the group"

    else:
        print("modelname not known") 

    friends = Friend.query.order_by(Friend.date_created)
    groups = Group.query.order_by(Group.date_created)
    return render_template('friends.html',title=title, friends = friends, groups = groups, modelName = modelName)

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