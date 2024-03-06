from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify #From the flask application, import Blueprint
from . import db
from .models import User, Session, SquadMembers #, Event, Goals, Times
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required
import sqlite3
from random import randint
import json

swimmerpages = Blueprint("swimmerPages", __name__)

#Function to check if a password is valid
def isValid(password):
    letter = any(c.isalpha() for c in password)
    digit = any(c.isdigit() for c in password)
    specialChar = any(not c.isalnum() for c in password)

    return letter and digit and specialChar 


### Pages for the swimmers ###

@login_required
@swimmerpages.route("/TodaySession") 
def swimmerTodaySession():
    user = User.query.filter_by(id=current_user.id).first()
    if user:
        name=current_user.forename.capitalize()
    else:
        name=""
    return render_template("swimmerTodaySession.html", name = name) 
   

@login_required
@swimmerpages.route("/PreviousSessions", methods=['GET', 'POST']) 
def swimmerSession():
    # if request.method == 'POST': 
        # entry = request.form.get('entry')#Gets the entry from the HTML 
        
        # if len(entry) < 1:
        #     flash('Entry is too short!', category='error') 
        # else:
        #     new_entry = Session(entry=entry, user_id=current_user.id)  #providing the schema for the note 
        #     db.session.add(new_entry) #adding the note to the database 
        #     db.session.commit()
        #     flash('Entry added!', category='success')
    return render_template("swimmerPreviousSessions.html", user=current_user)

@login_required
@swimmerpages.route("/Settings", methods=['GET', 'POST']) 
def swimmerSettings():
    squadMemberID = SquadMembers.query.filter_by(userID=current_user.id).first() #query the datbase for a user with the provided id
    squadID = squadMemberID.squadID
    if request.method == 'POST':
        forename = request.form['forename']
        surname = request.form['surname']
        squads_id = request.form['squads_id']
        password1 = request.form['password1']
        password2 = request.form['password2']
        
        if len(forename) != 0 and len(forename) < 2: #if invalid forename entered
            flash('First name must be greater than 1 character.', category='error') #flash error message
        elif len(surname) != 0 and len(surname) < 2: #if invalid surname entered
            flash('Surname must be greater than 1 character.', category='error') #flash error message
        elif len(password1) != 0 and len(password1) < 8: #if invalid password entered
            flash('Password must be at least 8 characters.', category='error') #flash error message
        elif password1 != password2: #if passwords don't match
            flash('Passwords don\'t match.', category='error') #flash error message
        elif len(password1) != 0 and not isValid(password1): #if invalid password entered
            flash('Password must contain letters, numbers and special characters.', category='error') #flash error message
        
        # If you want to update the password, handle it securely (e.g., hashing) before saving it.
        current_user.forename = forename #change forename
        current_user.surname = surname #change surname
        if len(password1) > 0: #if password is different
            current_user.password = generate_password_hash(password1, method='pbkdf2:sha256') #change password
        if squads_id != squadID:
            newSquadMember = SquadMembers(squadID=squads_id, userID=current_user.id)
        db.session.add(newSquadMember)

        db.session.commit() #save database
        flash('User information updated successfully.', 'success') #flash confirmation message
        return redirect(url_for('swimmerPages.swimmerSettings'))
    return render_template("swimmerSettings.html", user=current_user)

@login_required
@swimmerpages.route("/Goals", methods=["GET","POST"]) 
def swimmerGoals():
    # if request.method == 'POST': 
    #     goal = request.form.get('goal') #Gets the goal from the HTML 
    #     goaltype = request.form.get('goaltype')
        
    #     if len(goal) < 1:
    #         flash('Goal is too short!', category='error') 
    #     else:
    #         new_note = Goals(data=goal, user_id=current_user.id, goaltype=goaltype)  #providing the schema for the note 
    #         db.session.add(new_note) #adding the note to the database 
    #         db.session.commit()
    #         flash('Goal added!', category='success')
    #         pass
    return render_template("swimmerGoals.html")

# # Used to delete goals
# @swimmerpages.route('/delete-goal', methods=['POST'])
# def delete_goal():  
#     goal = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
#     goalID = goal['goalID']
#     goal = Goals.query.get(goalID)
#     if goal:
#         if goal.user_id == current_user.id:
#             db.session.delete(goal)
#             db.session.commit()

#     return jsonify({})

@login_required
@swimmerpages.route("/Competitions", methods={'GET','POST'}) 
def swimmerCompetitions():
    # events = Event.query.all()
    # if request.method == 'POST': 
    #     event = request.form.get('event')
    #     competition = request.form.get('competition')
    #     time = request.form.get('time')#Gets the goal from the HTML 
        
    #     if len(event) < 1:
    #         flash('Invalid entry!', category='error') 
    #     else:
    #         new_note = Times(event = event, time = time, competition = competition, user_id=current_user.id)  #providing the schema for the note 
    #         db.session.add(new_note) #adding the note to the database 
    #         db.session.commit()
    #         flash('Time added!', category='success')
    return render_template("swimmerCompetitions.html")

# #Used to delete times
# @swimmerpages.route('/delete-time', methods=['POST'])
# def delete_time():  
#     time = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
#     timeID = time['timeID']
#     time = Times.query.get(timeID)
#     if time:
#         if time.user_id == current_user.id:
#             db.session.delete(time)
#             db.session.commit()

#     return jsonify({})

@login_required
@swimmerpages.route("/Progression", methods={'GET', 'POST'})
def swimmerProgression():
    return render_template("swimmerProgression.html")