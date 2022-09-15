import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

import time
import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///fp.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    #User reached route via POST (clicking on a button with a post method)
    if request.method == "POST":

        #Require username
        if not request.form.get("username"):
            return false
        #Look if username is taken and apologize if it is
        lookusname = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(lookusname) != 0:
            return false
        else:
            username = request.form.get("username")

        #Require password
        if not request.form.get("password"):
            return false
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            return false
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))

        return redirect("/")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return false

        # Ensure password was submitted
        elif not request.form.get("password"):
            return false

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return false

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/home")

@app.route("/")
@login_required
def userhome():
    """ user homepage """
    
    """ Greet the user """
    user = session["user_id"]
    username = db.execute("SELECT username FROM users WHERE id = ?", user)
    session["username"] = username[0]["username"]

    """ Get the current day and date """
    x = datetime.datetime.now()
    day = x.strftime("%A")
    date = datetime.date.today()
    
    exists = db.execute("SELECT EXISTS ( SELECT name FROM sqlite_master WHERE type='table' AND name=?)", session["username"])
    for i in exists[0]:
        x = exists[0][i]
    if ( x == 1):
        user_table = db.execute("SELECT * FROM  ? ORDER BY t_id DESC", session["username"])
        tday = db.execute("SELECT DISTINCT type FROM ? WHERE day = ?", session["username"], day)
    else:
        user_table = False
        tday = False
    

    """ Your trainings tab"""
    trainings = db.execute("SELECT DISTINCT type FROM trainings WHERE user_id = ?", session["user_id"])
    return render_template("userhome.html", date=date, day=day, user_table=user_table, tday=tday, username=session["username"], exists=x, trainings=trainings)


@app.route("/train", methods=["GET", "POST"])
@login_required
def train():
    """ id comes from userhome via Your Trainings"""
    typ = request.args.get("type")
    trainings = db.execute("SELECT * FROM trainings WHERE user_id = ? AND type = ?", session["user_id"], typ)
    """ POST route from train.html form"""
    if request.method == "POST":
        typ = request.form.get("type")
        name = request.form.get("name")
        weight = request.form.get("weight")
        unit = request.form.get("unit")
        reps = request.form.get("reps")
        duration = request.form.get("duration")
        x = datetime.datetime.now()
        day = x.strftime("%A")
        current_date = datetime.date.today()
        db.execute("CREATE TABLE IF NOT EXISTS ? (t_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, type TEXT, name TEXT NOT NULL, weight NUMERIC, unit TEXT, reps NUMERIC, duration NUMERIC, current_date TEXT, day TEXT)", session["username"])
        db.execute("INSERT INTO ? (type, name, weight, unit, reps, duration, day, current_date) VALUES (?,?,?,?,?,?,?,?)", session["username"], typ, name, weight, unit, 
        reps, duration, day, current_date)
        return render_template("userhome.html", typ=typ)
    """GET route from userhome or any other"""
    return render_template("train.html", typ=typ, trainings=trainings)

@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        typ = request.form.get("type")
        name = request.form.get("name")
        training_day = request.form.get("training_day")
        db.execute("INSERT INTO trainings (user_id, type, name, training_day) VALUES (?,?,?,?)", session["user_id"], typ, name, training_day)
        return redirect("/")
    return render_template("new.html")