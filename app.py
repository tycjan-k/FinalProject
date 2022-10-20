import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
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

    #User reached route via POST (clicking on a button with a post method)
    if request.method == "POST":

        #Require username
        if not request.form.get("username"):
            error = True
            flash('You did not provide an username')
            return render_template("register.html", error=error)
        #Look if username is taken and apologize if it is
        lookusname = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(lookusname) != 0:
            error = True
            flash('Username is already taken')
            return render_template("register.html", error=error)
        else:
            username = request.form.get("username")

        #Require password
        if not request.form.get("password"):
            error = True
            flash('You did not provide a password')
            return render_template("register.html", error=error)
        password = request.form.get("password")

        #Confirm password
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            error = True
            flash('Passwords do not match')
            return render_template("register.html", error=error)

        #question and answer
        if request.form.get("question") and request.form.get("answer"):
            question = request.form.get("question")
            answer = request.form.get("answer")
            db.execute("INSERT INTO users (username, hash, question, answer) VALUES (?, ?, ?, ?)", username, generate_password_hash(password), question, answer)
        #Neither
        else:
            error = True
            flash('You need to provide safety question')
            return render_template("register.html", error=error)

        
        # Redirect user to home page
        flash('You successfully registered')
        return redirect("/home")

    #User got here via GET request
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            error = True
            flash('Empty username field')
            return render_template("login.html", error=error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = True
            flash('Empty password field')
            return render_template("login.html", error=error)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error = True
            flash('Wrong username or password')
            return render_template("login.html", error=error)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]


        # Greet the user
        user = session["user_id"]
        username = db.execute("SELECT username FROM users WHERE id = ?", user)
        session["username"] = username[0]["username"]

        flash('Welcome ' + session["username"] + '!')
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
    
    user = session["user_id"]
    #Get the current day and date
    x = datetime.datetime.now()
    day = x.strftime("%A")
    date = datetime.date.today()

    
    tday = db.execute("SELECT DISTINCT type FROM trainings WHERE user_id = ? AND training_day = ?", user, day)
    

    #Your trainings tab
    user_types = db.execute("SELECT DISTINCT type FROM trainings WHERE user_id = ?", user)
    trainings = db.execute("SELECT * FROM trainings WHERE user_id = ?", user)
    
    return render_template("userhome.html", date=date, day=day, tday=tday, 
    user_types=user_types, trainings=trainings)


@app.route("/train", methods=["GET", "POST"])
@login_required
def train():
    # id comes from userhome via Your Trainings
    typ = request.args.get("type")
    trainings = db.execute("SELECT * FROM trainings WHERE user_id = ? AND type = ?", session["user_id"], typ)
    error = None

    #POST route from train.html form
    if request.method == "POST":
        #type
        if not request.form.get("type"):
            flash('Training cancelled, there was no training type provided.')
            return redirect("/")
        typ = request.form.get("type")
        trainings = db.execute("SELECT * FROM trainings WHERE user_id = ? AND type = ?", session["user_id"], typ)
        #name
        if not request.form.get("name"):
            error = 'You need to provide a name.'
            return render_template("train.html", typ=typ, trainings=trainings, error=error)
        name = request.form.get("name")
        #weight
        if not request.form.get("weight"):
            error = 'You need to provide a weight.'
            return render_template("train.html", typ=typ, trainings=trainings, error=error)
        weight = request.form.get("weight")
        #unit
        if not request.form.get("unit"):
            error = 'You need to provide a weight unit.'
            return render_template("train.html", typ=typ, trainings=trainings, error=error)
        unit = request.form.get("unit")
        #reps
        if not request.form.get("reps"):
            error = 'You need to provide a number of repetitions.'
            return render_template("train.html", typ=typ, trainings=trainings, error=error)
        reps = request.form.get("reps")
        #other data
        duration = request.form.get("duration")
        x = datetime.datetime.now()
        day = x.strftime("%A")
        tdate = datetime.date.today()
        note = request.form.get("note")

        
        #get ID from trainings
        idt = db.execute("SELECT id FROM trainings WHERE type = ? AND name = ?", typ, name)
        idt = idt[0]['id']
        if not idt:
            error = 'Something went wrong, ID is empty.'
            return render_template("train.html", typ=typ, trainings=trainings, error=error)

        #sets
        sets = db.execute("SELECT COUNT(*) FROM exercises WHERE user_id = ? AND name = ? AND tdate = ?", session["user_id"], name, tdate)
        sets = sets[0]
        for i in sets:
            s = sets[i] + 1
            db.execute("UPDATE exercises SET sets = ? WHERE user_id = ? AND name = ? AND tdate = ?", s, session["user_id"], name, tdate)

        
        #Insert data into table
        db.execute("INSERT INTO exercises (idt, user_id, type, name, weight, unit, reps, duration, day, tdate, sets, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", idt, session["user_id"], typ, name, weight, unit, 
        reps, duration, day, tdate, s, note)
        #give feedback to the user
        flash('Set added')

    #GET route from userhome or any other
    return render_template("train.html", typ=typ, trainings=trainings)

@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    #empty error message
    error = None

    #Form
    if request.method == "POST":

        #type NOT NULL
        if (not request.form.get("type")) and (not request.form.get("custom_type")):
            error = 'You need to provide the type.'
            return render_template("new.html", error=error)
        elif (request.form.get("type") and request.form.get("custom_type")):
            error = 'You can only provide one type.'
            return render_template("new.html", error=error)
        elif request.form.get("type"):
            typ = request.form.get("type")
        elif request.form.get("custom_type"):
            typ = request.form.get("custom_type")
        else:
            error = 'Type not provided'

        #name NOT NULL
        if not request.form.get("name"):
            error = 'You need to provide the name.'
            return render_template("new.html", error=error)
        name = request.form.get("name")

        training_day = request.form.get("training_day")
        db.execute("INSERT INTO trainings (user_id, type, name, training_day) VALUES (?,?,?,?)", session["user_id"], typ, name, training_day)
        return redirect("/")
    return render_template("new.html")

@app.route("/filtr")
@login_required
def filtr():
    #return table data based of filtered training type
    user = session["user_id"]
    user_table = db.execute("SELECT * FROM exercises WHERE user_id = ? ORDER BY id DESC", user)
    user_trens = db.execute("SELECT DISTINCT idt, type, name, tdate, sets FROM exercises WHERE user_id = ? ORDER BY tdate DESC", user)
    cryt_type = request.args.get("cryt_type")
    if cryt_type == 'all':
        return render_template("all.html", user_table=user_table, user_trens=user_trens, cryt_type=cryt_type)

    #if cryt_type == type, then return all the exercises of a given type
    for training in user_trens:
        if cryt_type == training["type"]:
            return render_template("all.html", user_table=user_table, user_trens=user_trens, cryt_type=cryt_type)

    #if id is a concrete exercise id return just this exercise
    cryt_type = int(cryt_type)
    return render_template("filtr.html", user_table=user_table, user_trens=user_trens, cryt_type=cryt_type)

@app.route("/filtype")
@login_required
def filtype():
    # return trainings filtered by types
    user = session["user_id"]
    typ = request.args.get("type")
    #jeśli typ otrzymany typ to 'all' zwróć wszystkie treningi usera
    if typ == 'all':
        trainings = db.execute("SELECT * FROM trainings WHERE user_id = ?", user)
        #zmiana jednego na 'all' pozwala wybrać wszystkie danego typu. Nie szkodzi wypisaniu danych z trainings bo potrzebne są tylko 'name' i 'id'
        trainings[0]["type"] = 'all'
    else:
        trainings = db.execute("SELECT * FROM trainings WHERE user_id = ? AND type = ?", user, typ)
    return jsonify(trainings)

@app.route("/delete", methods=["POST"])
@login_required
def delete():
    #deleting the chosen training based on chosen ID
    idt = request.form.get("del_id")
    db.execute("DELETE FROM trainings WHERE id = ?", idt)
    flash('Training Deleted')
    return redirect("/")

@app.route("/progressroute")
@login_required
def progressroute():
    #get tid of the training
    p_id = request.args.get("progress_id")
    #daily sum of weight and reps of this type of exercise
    avg_weight = db.execute("SELECT avg(weight) FROM exercises WHERE idt = ? GROUP BY tdate ORDER BY tdate DESC", p_id)
    sum_reps = db.execute("SELECT sum(reps) FROM exercises WHERE idt = ? GROUP BY tdate ORDER BY tdate DESC", p_id)
    #dates of this type of exercise
    dates = db.execute("SELECT distinct tdate FROM exercises WHERE idt = ? ORDER BY tdate DESC", p_id)
    #number of days (trainings)
    ex_number = len(dates)

    table = []
    pbest = 0
    best_date = 0
    #look for daily progress
    for i in range(ex_number):
        #if its the last on the list (first ever exercise of this type)
        if i == ex_number-1:
            val = 10
            date = dates[i]["tdate"]
            weight = avg_weight[i]["avg(weight)"]
            reps = sum_reps[i]["sum(reps)"]
            #personal best
            if weight*reps > pbest:
                pbest = weight*reps
                best_date = date
            table.append({'date':date, 'weight':weight, 'reps':reps, 'val':val})
            return render_template("progress.html", table=table, best_date=best_date)
        #else compare to the next on the list (previous exercise in real time)
        date = dates[i]["tdate"]
        weight = avg_weight[i]["avg(weight)"]
        prev_weight = avg_weight[i+1]["avg(weight)"]
        if weight > prev_weight:
            w = 1
        elif weight == prev_weight:
            w = 0
        else:
            w = -2
        reps = sum_reps[i]["sum(reps)"]
        prev_reps = sum_reps[i+1]["sum(reps)"]
        if reps > prev_reps:
            r = 1
        elif reps == prev_reps:
            r = 0
        else:
            r = -2
        val = r + w
        #personal best
        if weight*reps > pbest:
            pbest = weight*reps
            best_date = date

        table.append({'date':date, 'weight':weight, 'reps':reps, 'val':val})
    #should not be needed 
    #return render_template("progress.html", table=table, best_date=best_date)

@app.route("/newq", methods=["GET", "POST"])
@login_required
def newq():
    #changing the security code/question
    if request.method == "POST":
        #question and answer
        if request.form.get("question") and request.form.get("answer"):
            question = request.form.get("question")
            answer = request.form.get("answer")
            db.execute("UPDATE users SET question = ?, answer = ? WHERE id = ?", question, answer, session["user_id"])
        #Neither of code, question and answer
        else:
            error = True
            flash('You need to provide question and answer')
            return render_template("newq.html", error=error)
        # Redirect user to home page
        flash('You successfully changed your settings')
        return redirect("/")

    #get route
    return render_template("newq.html")

@app.route("/who", methods=["GET", "POST"])
def who():
    if request.method == "POST":
        #didnt provide username
        if not request.form.get("username"):
            error = True
            flash('You need to provide username')
            return render_template("who.html", error=error)
        username = request.form.get("username")
        return redirect("/forgot?username=" + username)
    #get route
    return render_template("who.html")

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    #resetting password feature
    if request.method == "POST":
        #didnt provide username
        if not request.form.get("username"):
            error = True
            flash('You need to provide username')
            return render_template("forgot.html", error=error)
        username = request.form.get("username")

        #didnt provide neither answer
        if not request.form.get("answer"):
            error = True
            flash('You need to provide answer to the question')
            return render_template("forgot.html", error=error)
        #answer
        if request.form.get("answer"):
            answer = request.form.get("answer")
        else:
            answer = NULL
        answer_text = db.execute("SELECT answer FROM users WHERE username = ?", username)
        answer_text = answer_text[0]["answer"]
        #if correct log the user
        if answer_text == answer:
            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = ?", username)
            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]
            # Greet the user
            user = session["user_id"]
            username = db.execute("SELECT username FROM users WHERE id = ?", user)
            session["username"] = username[0]["username"]
            #redirect to set new password
            return redirect("/newpass")
        else:
            error = True
            flash('Wrong answer')
            return render_template("forgot.html")
    
    #Get route
    username = request.args.get("username")
    question = db.execute("SELECT question FROM users WHERE username = ?", username)
    question = question[0]["question"]
    return render_template("forgot.html", username=username, question=question)

@app.route("/newpass", methods=["GET", "POST"])
@login_required
def newpass():
    if request.method == "POST":
        if not (request.form.get("password") and request.form.get("confirmation")):
            error = True
            flash('You need to provide new password')
            return render_template("newpass.html", error=error)
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            error = True
            flash('Password and confirmation need to match!')
            return render_template("newpass.html", error=error)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(password), session["user_id"])
        return redirect("/")

    return render_template("newpass.html")

@app.route("/myaccount", methods=["GET"])
@login_required
def myaccount():
    return render_template("myaccount.html")
