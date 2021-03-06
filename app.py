from bson.objectid import ObjectId
from flask import (
    Flask, flash, render_template, redirect,
    request, session, url_for)
from flask_pymongo import PyMongo, DESCENDING
from forms import LoginForm, SignupForm, CreatePlacesForm, EditPlacesForm, ConfirmDelete
import math
import os
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


@app.errorhandler(404)
def handle_404(exception):
    return render_template('404.html', exception=exception)


@app.route('/edit_place/<place_id>', methods=['GET', 'POST'])
def edit_place(place_id):
    """Allows logged in user to edit their own recipes"""
    place_db = mongo.db.places.find_one_or_404({'_id': ObjectId(place_id)})
    if request.method == 'GET':
        form = EditPlacesForm(data=place_db)
        return render_template('edit_restaurant.html', recipe=place_db, form=form)
    form = EditPlacesForm(request.form)
    if form.validate_on_submit():
        places_db = mongo.db.places
        places_db.update_one({
            '_id': ObjectId(place_id),
        }, {
            '$set': {
                'name': request.form['name'],
                'city': request.form['city'],
                'added_by': session['username'],
                'description': request.form['description'],
                'tags': request.form['tags'],
                'image': request.form['image'],
            }
        })
        return redirect(url_for('home'))
    return render_template('edit_restaurant.html', place=place_db, form=form)


@app.route('/create_place', methods=['GET', 'POST'])
def create_place():
    """Creates a recipe and enters into recipe collection"""
    form = CreatePlacesForm(request.form)
    if form.validate_on_submit():
        # set the collection
        places_db = mongo.db.places
        # insert the new recipe
        places_db.insert_one({
            'name': request.form['name'],
            'city': request.form['city'],
            'added_by': session['username'],
            'description': request.form['description'],
            'tags': request.form['tags'],
            'image': request.form['image'],
            'views': 0
        })
        return redirect(url_for('home'))
    return render_template('create_restaurant.html', form=form)


@app.route('/delete_place/<place_id>', methods=['GET', 'POST'])
def delete_place(place_id):
    """Allows logged in user to delete one of their recipes with added confirmation"""
    place_db = mongo.db.places.find_one_or_404({'_id': ObjectId(place_id)})
    if request.method == 'GET':
        form = ConfirmDelete(data=place_db)
        return render_template('delete_restaurant.html', title="Delete Restaurant", form=form)
    form = ConfirmDelete(request.form)
    if form.validate_on_submit():
        places_db = mongo.db.places
        places_db.delete_one({
            '_id': ObjectId(place_id),
        })
        return redirect(url_for('home'))
    return render_template('delete_restaurant.html', place=place_db, form=form)


@app.route('/places')
def places():
    """Logic for recipe list and pagination"""
    # number of recipes per page
    per_page = 8
    page = int(request.args.get('page', 1))
    # count total number of recipes
    total = mongo.db.places.count_documents({})
    # logic for what recipes to return
    all_places = mongo.db.places.find().skip((page - 1)*per_page).limit(per_page)
    pages = range(1, int(math.ceil(total / per_page)) + 1)
    return render_template('restaurants.html', places=all_places, page=page, pages=pages, total=total)


@app.route('/search')
def search():
    """Provides logic for search bar"""
    query = request.args['query']
    # find instances of the entered word in title, tags or ingredients
    results = mongo.db.places.find({
        '$or': [
            {'name': {'$regex': query, '$options': 'i'}},
            {'tags': {'$regex': query, '$options': 'i'}},
            {'city': {'$regex': query, '$options': 'i'}},
        ]
    })
    return render_template('search.html', query=query, results=results)


if __name__ == '__main__':
    app.config['TRAP_BAD_REQUEST_ERRORS'] = False
    app.config['DEBUG'] = False
    app.run(host='127.0.0.1', debug=False)
