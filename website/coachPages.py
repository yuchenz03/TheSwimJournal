#importing all the dependencies
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify #From the flask application, import Blueprint
from . import db
from .models import User, Exercise, Squad #import the user, exercise and squad tables from the models page
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required
from random import randint
import json

#define a new blueprint named coachPages
coachpages = Blueprint("coachPages", __name__)

### Pages for the Coaches ###

#Function to check if a password is valid
def isValid(password):
    letter = any(c.isalpha() for c in password)
    digit = any(c.isdigit() for c in password)
    specialChar = any(not c.isalnum() for c in password)

    return letter and digit and specialChar 

#Route for the coach's dashboard page
@coachpages.route("/Dashboard")  
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachDashboard():
    user = User.query.filter_by(id=current_user.id).first() #ensure that a user with the current user's id exists
    if user: #If the user exists
        name=current_user.forename.capitalize() #retrieve the forename of the current user
    else: #if the user doesn't exist
        name="" #pass in empty string
    return render_template("coachDashboard.html", name=name) #render the coach dashboard template

#Route for the coach session page, supporting the post and get methods
@coachpages.route("/Session", methods=['POST','GET']) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachSession():
    # if request.method == 'POST': 
    #     exercisetype = request.form.get('exercisetype') #Gets the goal from the HTML 
    #     reps = request.form.get('reps')
        
    #     new_note = Exercise(name=exercisetype, user_id=current_user.id, reps=reps)  #providing the schema for the note 
    #     db.session.add(new_note) #adding the note to the database 
    #     db.session.commit()
    #     flash('Exercise added!', category='success')
    #rendering the coach session page
    return render_template("coachSession.html", user = current_user)

#Used to delete goals
@coachpages.route('/delete-exercise', methods=['POST'])
def delete_exercise():  
    exercise = json.loads(request.data) #this function expects a JSON from the INDEX.js file 
    exerciseID = exercise['exerciseID'] 
    exercise = Exercise.query.get(exerciseID)
    if exercise:
        if exercise.user_id == current_user.id:
            db.session.delete(exercise)
            db.session.commit()

    return jsonify({})

#route for the coach's my swimmers page, supporting get and post methods
@coachpages.route("/MySwimmers", methods = {'GET', 'POST'}) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachSwimmers():
    if current_user.squadID: 
        squadid = current_user.squadID
        squad = Squad.query.get(squadid)
        members = User.query.filter_by(squadID=squadid).all()
        if squad is None:
            # Handle the case where the squad does not exist
            squad=[]
        if members is None:
            # Handle the case where there are no members
            members=[]
        
    else:
        squad=""
        members=[]
        squadCode=0
    if request.method == 'POST': 
        squadName = request.form.get('squadName')
        squadName_exists = Squad.query.filter_by(squadName=squadName).first()
        
        if squadName_exists:
            flash("Squad name already in use.", category="error")
        elif len(squadName) < 2:
            flash("Squad name too short.", category="error")
        else:
            flash("Squad successfully created")
            squadCode = randint(1000,9999)
            new_squad = Squad(id=squadCode, squadName=squadName)
            db.session.add(new_squad)
            db.session.commit()
    
            squad_id = squadCode
            current_user.squadID = squad_id
            db.session.commit()
        
            squad = Squad.query.get(squad_id)

    return render_template("coachSwimmers.html", user=current_user, squad=squad,members=members)

@coachpages.route("/Journal")
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachJournal():
    # if request.method == 'POST': 
    #     entry = request.form.get('entry')#Gets the entry from the HTML 
        
    #     if len(entry) < 1:
    #         flash('Entry is too short!', category='error') 
    #     else:
    #         new_entry = Journal(entry=entry, user_id=current_user.id)  #providing the schema for the note 
    #         db.session.add(new_entry) #adding the note to the database 
    #         db.session.commit()
    #         flash('Entry added!', category='success')
            
    return render_template("coachJournal.html", user=current_user)


@coachpages.route("/Settings", methods=['GET', 'POST']) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachSettings():
    if request.method == 'POST':
        forename = request.form['forename']
        surname = request.form['surname']
        password1 = request.form['password1']
        password2 = request.form['password2']
        
        if len(forename) != 0 and len(forename) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(surname) != 0 and len(surname) < 2:
            flash('Surname must be greater than 1 character.', category='error')
            flash('Passwords don\'t match.', category='error')
        elif len(password1) != 0 and len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) != 0 and not isValid(password1):
            flash('Password must contain letters, numbers and special characters.', category='error')
        
        # If you want to update the password, handle it securely (e.g., hashing) before saving it.
        if len(forename) > 0:
            current_user.forename = forename
        if len(surname) > 0:
            current_user.surname = surname
        if len(password1) > 0:
            current_user.password = generate_password_hash(password1, method='sha256')

        db.session.commit()
        flash('User information updated successfully.', 'success')
        return redirect(url_for('coachPages.coachSettings'))
    return render_template("coachSettings.html", user=current_user)

@coachpages.route("/Attendance") 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachAttendance():
    return render_template("coachAttendance.html")