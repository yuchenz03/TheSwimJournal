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
                if user.role == "Swimmer":
                    return redirect(url_for('swimmerPages.swimmerDashboard'))
                elif user.role == "Coach":
                    return redirect(url_for('coachPages.coachDashboard'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/securityQuestion', methods=['GET','POST'])
def securityQuestion():
    if request.method == 'POST':
        SQNum = request.form.get('SQNum')
        SQAnswer = request.form.get('SQAnswer')
        if len(SQNum) < 1:
            flash('Choose a security question.', category='error')
        if len(SQAnswer) < 1:
            flash('Submit an answer to the security question.', category='error')
        else:
            current_user.SQnum = SQNum
            current_user.SQans = SQAnswer
            db.session.commit()
            if current_user.role == "Swimmer":
                return redirect(url_for('swimmerPages.swimmerDashboard'))
            elif current_user.role == "Coach":
                return redirect(url_for('coachPages.coachDashboard'))
    
    return render_template("securityQuestion.html", user=current_user)

@auth.route('/resetPassword', methods=['GET','POST'])
def resetPassword():
    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        SQans = request.form.get('SQans')
        if len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif not isValid(password1):
            flash('Password must contain letters, numbers and special characters.', category='error')
        else:
            current_user.password = generate_password_hash(password1, method='sha256')
            db.session.commit()
            logout_user()
            return redirect(url_for('auth.login'))
    return render_template("resetPassword.html", user=current_user)

@auth.route('/enterEmail', methods=['GET','POST'])
def enterEmail():
    if request.method == 'POST':
        email = request.form.get('email')
        
        user = User.query.filter_by(email=email).first()
        login_user(user, remember=True)
        flash('If there is an account connected to this email address, you will be redirected', category='success')
        if user:
            return redirect(url_for('auth.resetPassword'))

    return render_template("enterEmail.html", user=current_user)

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
        role = "Coach"

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
            return redirect(url_for('auth.securityQuestion'))

    return render_template("coachSignup.html", user=current_user)

@auth.route('/swimmerSignup', methods=['GET', 'POST'])
def swimmer_sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        forename = request.form.get('forename')
        surname = request.form.get('surname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = "Swimmer"

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
            return redirect(url_for('auth.securityQuestion'))

    return render_template("swimmerSignup.html", user=current_user)



@auth.route('/calendar', methods=['GET', 'POST'])
def calendar():
    return render_template("calendar.html", user=current_user)
