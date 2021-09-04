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


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login handler"""
    if session.get('logged_in'):
        if session['logged_in'] is True:
            return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        # get all users
        users = mongo.db.users
        # try and get one with same name as entered
        db_user = users.find_one({'username': request.form['username']})
        if db_user:
            # check password using hashing
            if bcrypt.hashpw(request.form['password'].encode('utf-8'),
                             db_user['password']) == db_user['password']:
                session['username'] = request.form['username']
                session['logged_in'] = True
                # successful redirect to home logged in
                return redirect(url_for('home', form=form))
            # must have failed set flash message
            flash('Invalid username/password combination')
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    """Clears session and redirects to home"""
    session.clear()
    return redirect(url_for('home'))


@app.route('/place/<place_id>')
def place(place_id):
    """Shows full recipe and increments view"""
    mongo.db.places.find_one_and_update(
        {'_id': ObjectId(place_id)},
        {'$inc': {'view': 1}}
    )
    place_db = mongo.db.places.find_one_or_404({'_id': ObjectId(place_id)})
    return render_template('place.html', place=place_db)

