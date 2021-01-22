from flask import Flask,render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# import smtplib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friends.db'
#initialize database
db = SQLAlchemy(app)

#create database model
class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    #create function to return stringwhen we add something
    def __repr__(self):
        return '<Name %r>' % self.id



subscribers = []

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/about')
def about():
    
    names = ["Mr Brown","Turing","Gates"]
    return render_template('about.html',names=names)

@app.route('/friends' , methods=["POST","GET"])
def friends():
    
    title = "my friends"
    if request.method == "POST":
        friend_name = request.form['name']
        new_friend = Friend(name=friend_name)
        #push to databse
        try:
            db.session.add(new_friend)
            db.session.commit()
            return redirect('/friends')
        except:
            return "there was error adding your friend"
    else:
        friends = Friend.query.order_by(Friend.date_created)
        return render_template('friends.html',title=title, friends = friends)

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