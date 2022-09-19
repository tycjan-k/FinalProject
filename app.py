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

    #Empty error message
    error = None

    #User reached route via POST (clicking on a button with a post method)
    if request.method == "POST":

        #Require username
        if not request.form.get("username"):
            error = 'You did not provide an username'
            return render_template("register.html", error=error)
        #Look if username is taken and apologize if it is
        lookusname = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(lookusname) != 0:
            error = 'Username is already taken'
            return render_template("register.html", error=error)
        else:
            username = request.form.get("username")

        #Require password
        if not request.form.get("password"):
            error = 'You did not provide a password'
            return render_template("register.html", error=error)
        password = request.form.get("password")

        #Confirm password and add it to the users table
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            error = 'Passwords do not match'
            return render_template("register.html", error=error)
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
        # Redirect user to home page
        flash('You successfully registered')
        return redirect("/home")

    #User got here via GET request
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    #create empty error message 
    error = None

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            error = 'Empty username field'
            return render_template("login.html", error=error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = 'Empty password field'
            return render_template("login.html", error=error)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error = 'Wrong username or password'
            return render_template("login.html", error=error)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash('you logged in')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/home")

@app.route("/")
@login_required
def userhome():
    """ user homepage """
    # Greet the user
    user = session["user_id"]
    username = db.execute("SELECT username FROM users WHERE id = ?", user)
    session["username"] = username[0]["username"]

    #Get the current day and date
    x = datetime.datetime.now()
    day = x.strftime("%A")
    date = datetime.date.today()

    user_table = db.execute("SELECT * FROM exercises WHERE user_id = ? ORDER BY t_id DESC", user)
    tday = db.execute("SELECT DISTINCT type FROM trainings WHERE user_id = ? AND training_day = ?", user, day)
    user_trens = db.execute("SELECT DISTINCT type, name, tdate, sets FROM exercises WHERE user_id = ?", user)

    #Your trainings tab
    trainings = db.execute("SELECT DISTINCT type FROM trainings WHERE user_id = ?", session["user_id"])

        
    return render_template("userhome.html", date=date, day=day, user_table=user_table, user_trens=user_trens, tday=tday, username=session["username"], trainings=trainings)


@app.route("/train", methods=["GET", "POST"])
@login_required
def train():
    # id comes from userhome via Your Trainings
    typ = request.args.get("type")

    #POST route from train.html form
    if request.method == "POST":
        typ = request.form.get("type")
        name = request.form.get("name")
        weight = request.form.get("weight")
        unit = request.form.get("unit")
        reps = request.form.get("reps")
        duration = request.form.get("duration")
        x = datetime.datetime.now()
        day = x.strftime("%A")
        tdate = datetime.date.today()
        #sets
        sets = db.execute("SELECT COUNT(*) FROM exercises WHERE user_id = ? AND name = ? AND tdate = ?", session["user_id"], name, tdate)
        sets = sets[0]
        for i in sets:
            s = sets[i] + 1
            db.execute("UPDATE exercises SET sets = ? WHERE user_id = ? AND name = ? AND tdate = ?", s, session["user_id"], name, tdate)
        #Insert data into table
        db.execute("INSERT INTO exercises (user_id, type, name, weight, unit, reps, duration, day, tdate, sets) VALUES (?,?,?,?,?,?,?,?,?,?)", session["user_id"], typ, name, weight, unit, 
        reps, duration, day, tdate, s)
        #give feedback to the user
        flash('Set added')

    #GET route from userhome or any other

    trainings = db.execute("SELECT * FROM trainings WHERE user_id = ? AND type = ?", session["user_id"], typ)
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