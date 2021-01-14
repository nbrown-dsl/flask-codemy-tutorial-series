from flask import Flask,render_template

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    title = "Flask starter project"
    return render_template('index.html', title=title)

@app.route('/about')
def about():
    names = ["Mr Brown","Turing","Gates"]
    return render_template('about.html',names=names)
