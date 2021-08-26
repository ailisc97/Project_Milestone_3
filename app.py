import os
from flask import (
    Flask, flash, render_template, redirect,
    request, session, url_for)
from flask_pymongo import PyMongo
from datetime import datetime, date

if os.path.exists("env.py"):
    import env

app = Flask(__name__)
csrf = CSRFProtect(app)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

@app.route("/")
@app.route("/home")
def home():
    """
    Renders home page template when going to the main website link
    """
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Sign up page, allows users to register for an account
    if username doesn't already exist.
    """
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("This user name already exists.", 'error')
            return redirect(url_for("signup"))

        new_user = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "name": request.form.get("name").lower()
        }
        # Insert new user into users collection
        mongo.db.users.insert_one(new_user)

        session["user"] = request.form.get("username").lower()
        # Display flash success message on screen
        flash("Registration Successful!", 'message')
        return redirect(url_for(
                    "profile", username=session["user"]))

    return render_template("signup.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    """
    Checks users collection for user and password to allow registered
    users to sign in. Redirects to profile on successful sign in.
    """
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        # Check if user exists and that password matches.
        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash(f"Welcome, {session['user']}", 'message')
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password", 'error')
                return redirect(url_for("signin"))

        else:
            flash("Incorrect Username and/or Password", 'error')
            return redirect(url_for("signin"))

    return render_template("signin.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    """
    Takes the session user's username from 'users' database
    and returns them to their profile page. Returns events
    created by the user.
    """
    username = mongo.db.users.find_one(
        {"username": session["user"]})

    if session["user"]:
        events = list(mongo.db.events.find().sort("date"))
        # Filters events that were created by the user
        events = list(filter
                      (lambda x: x['created_by'] == username['username'],
                       events))
        return render_template("profile.html",
                               username=username, events=events)

    return redirect(url_for("signin"))


@app.route("/signout")
def signout():
    """
    Removes logged in user from session cookie and
    returns them to the signin page.
    """
    flash("You have been signed out", 'message')
    session.pop("user")
    return redirect(url_for("signin"))
