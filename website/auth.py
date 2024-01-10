#importing all the dependencies
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User #importing the user class from the models page
from werkzeug.security import generate_password_hash, check_password_hash #
from . import db   #from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user

#define a new blueprint named auth
auth = Blueprint('auth', __name__)

#Function to check if a password is valid
def isValid(password): 
    letter = any(c.isalpha() for c in password) #checks if the password contains alphabetic characters
    digit = any(c.isdigit() for c in password) #checks if the password contains digits
    specialChar = any(not c.isalnum() for c in password) #checks if the password contains any special characters

    return letter and digit and specialChar #return True if all conditions satisfied, otherwise False


@auth.route("/") #create a blueprint for whenever the app is called with / as its location
@auth.route("/home") #Having two @pages.route() for one function indicates that there is one page that is returned for these two locations.
def homepage():
    return render_template("homepage.html") #the page associated with the above routes


@auth.route('/login', methods=['GET', 'POST']) #route for the login page, supporting both get and post methods
def login():
    if request.method == 'POST': #if the method is post
        email = request.form.get('email') #retrieve the email entered in login form
        password = request.form.get('password') #retrieve password entered in login form

        user = User.query.filter_by(email=email).first() #query the datbase for a user with the provided email
        if user: #if there exists such user
            if check_password_hash(user.password, password): #check if the hashed value of the entered password equals the hashed value of user password
                flash('Logged in successfully!', category='success') #flash a success message
                login_user(user, remember=True) #and login the user
                if user.role == "Swimmer": #if the user's role is swimmer
                    return redirect(url_for('swimmerPages.swimmerDashboard')) #redirect to the swimmer's dashboard
                elif user.role == "Coach": #if the user's role is coach
                    return redirect(url_for('coachPages.coachDashboard')) #redirect to the coach's dashboard
            else: #Otherwise, if the password is incorrect,
                flash('Incorrect password, try again.', category='error') #flash an error message
        else: #if there doesn't exist a user with that email
            flash("No user found.", category='error') #flash an error message

    return render_template("login.html", user=current_user) #render the login page template

@auth.route('/securityQuestion', methods=['GET','POST']) #route for the page to set a security question, supporting both get and post methods
def securityQuestion():
    if request.method == 'POST': #if method is post, then
        SQquestion = request.form.get('SQquestion') #retrieve the security question from the form
        SQans = request.form.get('SQanswer') #retrieve the security answer from the form
        if len(SQquestion) < 1: #if no security question was chosen
            flash('Choose a security question.', category='error') #flash an error message 
        if len(SQans) < 1: #if no answer was given
            flash('Submit an answer to the security question.', category='error') #flash an error message
        else: #if both the security question and answer are valid
            current_user.SQquestion = SQquestion #set the user's security question
            current_user.SQans = SQans #set the user's security answer
            db.session.commit() #save these changes to the database
            if current_user.role == "Swimmer": #if user is a swimmer
                return redirect(url_for('swimmerPages.swimmerDashboard')) #redirect to the swimmer's dashboard
            elif current_user.role == "Coach": #if user is a coach
                return redirect(url_for('coachPages.coachDashboard')) #redirect to the coach's dashboard
    
    return render_template("securityQuestion.html", user=current_user) #render the security question page template

#route for resetting password, supporting get and post methods
@auth.route('/resetPassword', methods=['GET','POST']) 
def resetPassword():
    email = session.get('email') #retrieve the email stored in the flask session
    user = User.query.filter_by(email=email).first() #retrieving the user with that email from the database
    
    if request.method == 'POST': #if method is post
        password1 = request.form.get('password1') #retrieve the new password entered from the form
        password2 = request.form.get('password2') #retrieve the new password re-entered from the form
        userans = request.form.get('userans') #retrieve the security question answer from the form
        if userans == user.SQans: #If the security question answer is correct
            if len(password1) < 8: #If the length of the new password is less than 8
                flash('Password must be at least 8 characters.', category='error') #flash an error message
            elif not isValid(password1): #If the password is not valid (function above)
                flash('Password must contain letters, numbers and special characters.', category='error') #flash an error message
            elif password1 != password2: #If the new passwords don't match
                flash('Passwords don\'t match.', category='error') #flash an error message
            else: #If all tests have been passed
                user.password = generate_password_hash(password1, method='sha256') #Hash the new password
                db.session.commit() #save the changes to the database
                flash('Password changed successfully.', category='success') #Flash confirmation message
                return redirect(url_for('auth.login')) #redirect the user to the login page
        else: #If the security question is incorrect
            flash('Security question answer is incorrect.', category='error') #Flash an error message
    return render_template("resetPassword.html", question = user.SQquestion) #Render the reset password template and pass in the security question

#Route for entering the email for password reset
@auth.route('/enterEmail', methods=['GET','POST']) 
def enterEmail(): 
    if request.method == 'POST': #If method type is post
        email = request.form.get('email') #retrieve the user's email from the form
        
        user = User.query.filter_by(email=email).first() #attempt to find the user account associated with the email
        flash('If there is an account connected to this email address, you will be redirected', category='success') #Flash confirmation message
        if user: #If a user account has been found
            session['email'] = email #add the email entered to the session
            return redirect(url_for('auth.resetPassword')) #redirect the user to the reset password page.
        #If no user has been found, stay on the current page.

    return render_template("enterEmail.html") #render the enter email page template

#route for the page to log out the user
@auth.route('/logout')
@login_required #decorator to ensure that only logged in users can log out. Otherwise, redirect to login page.
def logout(): 
    logout_user() #flask method ot log out the current user
    return redirect(url_for('auth.homepage')) #Redirect the user to the homepage.

#route for coach sign-up, supporting both get and post methods
@auth.route('/coachSignup', methods=['GET', 'POST'])
def coach_sign_up():
    if request.method == 'POST': #if the method type is post:
        email = request.form.get('email').lower() #retrieve the data from the sign-up page form
        forename = request.form.get('forename')
        surname = request.form.get('surname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = "Coach" #Since they are creating a coach account, set the user's role to be coach

        user = User.query.filter_by(email=email).first() #Check if there are any existing users with this email
        if user: #If a user with the entered email exists
            flash('Email already in use.', category='error') #Flash an error message
            return render_template("coachSignup.html", user=current_user) #render coach-signup template/
        if '@' not in email: #If the email does not contain an @ symbol
            flash('Must be valid email!', category='error') #Flash an error message
        elif len(email) < 4: #If the length of the email is less than four
            flash('Email must be greater than 3 characters.', category='error') #Flash an error message
        elif len(forename) < 2: #if length of forename invalid
            flash('First name must be greater than 1 character.', category='error') #flash an error message
        elif len(surname) < 2: #if length of surname invalid
            flash('Surname must be greater than 1 character.', category='error') #flash an error message
        elif password1 != password2: #If the entered passwords don't match
            flash('Passwords don\'t match.', category='error') #flash an error message
        elif len(password1) < 8: #If the length of the password is less than 8
            flash('Password must be at least 8 characters.', category='error') #flash an error message
        elif not isValid(password1): #If the password is invalid (based on function above)
            flash('Password must contain letters, numbers and special characters.', category='error') #flash an error message
        else: #If all requirements are met
            new_user = User(email=email, forename=forename, surname=surname, password=generate_password_hash( 
                password1, method='sha256'), role=role) #Hash the password and create a new user with this information
            db.session.add(new_user) #add this user to the database
            db.session.commit() #save the database
            login_user(new_user, remember=True) #login the new user
            flash('Account created!', category='success') #Flash a confirmation message
            return redirect(url_for('auth.securityQuestion')) #redirect the user to security question page to set security question

    return render_template("coachSignup.html", user=current_user) #render coach-signup template/

#Route for swimmer sign-up, supporting both get and post methods
#The code for this page is extremely similar to the coach sign-in page, so I will only comment different lines
@auth.route('/swimmerSignup', methods=['GET', 'POST'])
def swimmer_sign_up():
    if request.method == 'POST': 
        email = request.form.get('email').lower()
        forename = request.form.get('forename')
        surname = request.form.get('surname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = "Swimmer" #Rather than the role of the user being coach, it is swimmer

        user = User.query.filter_by(email=email).first() 
        if user:
            flash('Email already in use.', category='error')
            return render_template("coachSignup.html", user=current_user) #render coach-signup template/
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
    #render the template for the swimmer sign up page
    return render_template("swimmerSignup.html", user=current_user)
