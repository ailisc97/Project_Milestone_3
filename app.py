import math
import os

from bson import ObjectId
from flask import (
    Flask, flash, render_template, redirect,
    request, session, url_for)
from flask_pymongo import PyMongo, DESCENDING
from forms import LoginForm, SignupForm, CreatePlacesForm, EditPlacesForm, ConfirmDelete
import bcrypt

if os.path.exists("env.py"):
    import env

app = Flask(__name__)

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
   four_places_to_eat = mongo.db.places.find().sort([('views', DESCENDING)]).limit(4)
   return render_template('index.html', places=four_places_to_eat)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handles registration functionality"""
    form = SignupForm(request.form)
    if form.validate_on_submit():
        # get all the users
        users = mongo.db.users
        # see if we already have the entered username
        existing_user = users.find_one({'username': request.form['username']})

        if existing_user is None:
            # hash the entered password
            hash_pass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            # insert the user to DB
            users.insert_one({'username': request.form['username'],
                          'password': hash_pass})
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        # duplicate username set flash message and reload page
        flash('Sorry, that username is already taken - use another')
        return redirect(url_for('signup'))
    return render_template('signup.html', form=form)


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
   and returns them to their profile page. Returns resturants
   created by the user.
   """
   username = mongo.db.users.find_one(
       {"username": session["user"]})

   if session["user"]:
       resturants = list(mongo.db.places.find())
      # Filters  that were created by the user
       resturants = list(filter
                     (lambda x: x['created_by'] == username['username'],
                      resturants))
       return render_template("profile.html",
                              username=username, resturants=resturants)

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
