###CORRECTED###


from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   #means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

#Checking if a password is valid
def isValid(password):
    letter = any(c.isalpha() for c in password)
    digit = any(c.isdigit() for c in password)
    specialChar = any(not c.isalnum() for c in password)

    return letter and digit and specialChar


@auth.route("/") #create a blueprint for whenever the app is called with / as its location
@auth.route("/home") #Having two @pages.route() for one function indicates that there is one page that is returned for these two locations.
def homepage():
    return render_template("homepage.html")
    #To pass in a variable from the backend to the frontend, do this:
    #return render_template("home.html", name = 1). If you then place this {{name}} into the specified html page, it will return
    #the value of that variable.


@auth.route('/login', methods=['GET', 'POST']) #Creates a blueprint for whenever 
#the app is called with /login as its location
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                if user.role == "swimmer":
                    return redirect(url_for('swimmerPages.swimmerDashboard'))
                elif user.role == "coach":
                    return redirect(url_for('coachPages.coachDashboard'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.homepage'))


@auth.route('/coachSignup', methods=['GET', 'POST'])
def coach_sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        forename = request.form.get('forename')
        surname = request.form.get('surname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = "coach"

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        if '@' not in email:
            flash('Must be valid email!', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(forename) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(surname) < 2:
            flash('Surname must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        elif not isValid(password1):
            flash('Password must contain letters, numbers and special characters.', category='error')
        else:
            new_user = User(email=email, forename=forename, surname=surname, password=generate_password_hash(
                password1, method='sha256'), role=role)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('coachPages.Dashboard'))

    return render_template("coachSignup.html", user=current_user)

@auth.route('/swimmerSignup', methods=['GET', 'POST'])
def swimmer_sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        forename = request.form.get('forename')
        surname = request.form.get('surname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = "swimmer"

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        if '@' not in email:
            flash('Must be valid email!', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(forename) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(surname) < 2:
            flash('Surname must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        elif not isValid(password1):
            flash('Password must contain letters, numbers and special characters.', category='error')
        else:
            new_user = User(email=email, forename=forename, surname=surname, password=generate_password_hash(
                password1, method='sha256'), role=role)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('swimmerPages.swimmerDashboard'))

    return render_template("swimmerSignup.html", user=current_user)