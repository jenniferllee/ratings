"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, redirect, request, flash,
                   session)

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
    """Show form for user to enter email and password.

    If user is already registered, user becomes logged in.
    If user is new to site, new user is created in database."""

    return render_template("user_login.html")


@app.route("/login-success", methods=['POST'])
def handle_login_form():
    """Handle login submission and redirect to homepage."""

    email = request.form.get("email")
    password = request.form.get("password")

    all_emails = db.session.query(User.email).all()
    print all_emails

    if email in all_emails:
        db_password = db.session.query(User.password).filter(User.email == email).one()
        print db_password
        # if password == db_password:
        #     # login
        # else:
        #     # error
    else:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

    return redirect("/")  # email=email, password=password)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
