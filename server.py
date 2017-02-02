"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, redirect, request, flash,
                   session, url_for)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db

from datetime import datetime


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


@app.route("/users/user-page/")              # /<user_id>
def show_user_page():
    """Displays user info."""

    user_id = request.args.get("user_id")   # if ^, comment out this line
    user = db.session.query(User).filter(User.user_id == user_id).first()

    title_and_rating = db.session.query(Movie.title, Rating.score).filter((Rating.user_id == user_id) &
                                                                          (Rating.movie_id == Movie.movie_id)).all()

    return render_template("user_page.html",
                           user=user,
                           title_and_rating=title_and_rating)


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)


@app.route("/movies/movie-page")
def show_movie_page():
    """Displays movie info."""

    movie_id = request.args.get("movie_id")
    movie = db.session.query(Movie).filter(Movie.movie_id == movie_id).first()
    movie.released_at = movie.released_at.strftime("%B %d, %Y")

    rating_list = db.session.query(User.user_id, Rating.score).filter((Movie.movie_id == movie_id) &
                                                                      (Rating.movie_id == Movie.movie_id) &
                                                                      (Rating.user_id == User.user_id)).all()

    return render_template("movie_page.html",
                           movie=movie,
                           rating_list=rating_list)


@app.route("/movie-add-success", methods=["POST"])
def add_rating():
    """Add new rating to database or update existing rating."""

    movie_id = request.form.get("movie-id")
    user_rating = request.form.get("user-rating")
    user_id = session['Logged in user']

    rating_by_user = db.session.query(Rating.user_id).filter((Rating.movie_id == movie_id) &
                                                             (Rating.user_id == user_id)).first()

    if rating_by_user:
        # update rating
        rating_to_update = db.session.query(Rating).filter((Rating.user_id == user_id) &
                                                           (Rating.movie_id == movie_id)).first()
        setattr(rating_to_update, 'score', user_rating)

    else:
        # add new rating
        rating_to_add = Rating(user_id=user_id,
                               movie_id=movie_id,
                               score=user_rating)
        db.session.add(rating_to_add)

    db.session.commit()

    return redirect(url_for("show_movie_page", movie_id=movie_id))


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
