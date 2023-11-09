from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify #From the flask application, import Blueprint
from . import db
from .models import User, Exercise, Squad
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required
import sqlite3
from random import randint
import json

coachpages = Blueprint("coachPages", __name__)

### Pages for the Coaches ###

def isValid(password):
    letter = any(c.isalpha() for c in password)
    digit = any(c.isdigit() for c in password)
    specialChar = any(not c.isalnum() for c in password)

    return letter and digit and specialChar 

@login_required
@coachpages.route("/Dashboard")
def coachDashboard():
    user = User.query.filter_by(id=current_user.id).first()
    if user: 
        name=current_user.forename.capitalize()
    else:
        name=""
    return render_template("coachDashboard.html", name=name) #, name = name
    #To pass in a variable from the backend to the frontend, do this:
    #return render_template("home.html", name = 1). If you then place this {{name}} into the specified html page, it will return
    #the value of that variable.
    #return render_template("coachDashboard.html")


@login_required
@coachpages.route("/Session", methods=['POST','GET']) 
def coachSession():
    # if request.method == 'POST': 
    #     exercisetype = request.form.get('exercisetype') #Gets the goal from the HTML 
    #     reps = request.form.get('reps')
        
    #     new_note = Exercise(name=exercisetype, user_id=current_user.id, reps=reps)  #providing the schema for the note 
    #     db.session.add(new_note) #adding the note to the database 
    #     db.session.commit()
    #     flash('Exercise added!', category='success')
    return render_template("coachSession.html", user = current_user)

#Used to delete goals
@coachpages.route('/delete-exercise', methods=['POST'])
def delete_exercise():  
    exercise = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    exerciseID = exercise['exerciseID']
    exercise = Exercise.query.get(exerciseID)
    if exercise:
        if exercise.user_id == current_user.id:
            db.session.delete(exercise)
            db.session.commit()

    return jsonify({})

@login_required
@coachpages.route("/MySwimmers", methods = {'GET', 'POST'}) 
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
            squadCode = randint(1000,9999)
            new_squad = Squad(id=squadCode, squadName=squadName)
            db.session.add(new_squad)
            db.session.commit()
    
            squad_id = squadCode
            current_user.squadID = squad_id
            db.session.commit()
        
            squad = Squad.query.get(squad_id)

    return render_template("coachSwimmers.html", user=current_user, squad=squad,members=members)

@login_required
@coachpages.route("/Journal") 
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


@login_required
@coachpages.route("/Settings", methods=['GET', 'POST']) 
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

@login_required
@coachpages.route("/Attendance") 
def coachAttendance():
    return render_template("coachAttendance.html")