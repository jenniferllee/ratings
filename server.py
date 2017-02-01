"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, redirect, request, flash,
                   session, url_for)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/login")
def user_login():
    """Show form for user to enter email and password."""

    return render_template("user_login.html")


@app.route("/login-success", methods=['POST'])
def handle_login_form():
    """Handle login submission and redirect to homepage.

    If user is already registered, user becomes logged in.
    If user is new to site, user is directed to registration."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = db.session.query(User).filter(User.email == email).first()
    print user

    if user:
        if password == user.password:
            session['Logged in user'] = user.user_id    # add user id to Flask session
            flash("Logged in.")
            return redirect(url_for('show_user_page', user_id=session['Logged in user']))
        else:
            flash("Invalid password.")
            return redirect("/login")
    else:
        flash("You are not registered with us.")
        return redirect("/register")


@app.route("/register")
def register():
    """Show form for user to register."""

    return render_template("register.html")


@app.route("/register-success", methods=["POST"])
def handle_registration_form():
    """Handle registration submission and redirect to login page."""

    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    zipcode = request.form.get("zip")

    user = db.session.query(User).filter(User.email == email).first()

    if user:
        flash("You are already registered. Please log in.")
        return redirect("/login")
    else:
        new_user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please log in.")
        return redirect("/login")


@app.route("/logout")
def logout():
    """Logs user out and removes user ID from session."""

    del session['Logged in user']
    print session

    flash("Logged out")
    return redirect("/")


@app.route("/users/user-page")      # /<user_id>
def show_user_page():
    """Displays user info."""

    user_id = request.args.get("user_id")
    user = db.session.query(User).filter(User.user_id == user_id).first()

    movie_titles = db.session.query(Movie.title).filter((Rating.user_id == user_id) &
                                                        (Rating.movie_id == Movie.movie_id)).all()
    movie_titles = [i[0] for i in movie_titles]

    ratings = db.session.query(Rating.score).join(Movie).filter(Rating.user_id == user_id).all()
    ratings = [i[0] for i in ratings]

    title_and_rating = zip(movie_titles, ratings)

    return render_template("user_page.html",
                           user=user,
                           title_and_rating=title_and_rating)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
