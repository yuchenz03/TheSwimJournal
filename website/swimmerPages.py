from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session #From the flask application, import Blueprint
from . import db
from .models import User, Session, SquadMembers, Squad, Event, SwimmerSession
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required
import sqlite3
from random import randint
import json
from datetime import date, time, datetime

swimmerpages = Blueprint("swimmerPages", __name__)

#Function to check if a password is valid
def isValid(password):
    letter = any(c.isalpha() for c in password)
    digit = any(c.isdigit() for c in password)
    specialChar = any(not c.isalnum() for c in password)

    return letter and digit and specialChar 


### Pages for the swimmers ###

@login_required
@swimmerpages.route("/TodaySession", methods=['GET','POST']) 
def swimmerTodaySession():
    user = User.query.filter_by(id=current_user.id).first()
    if user:
        name=current_user.forename.capitalize()
    else:
        name=""
    currtoday = date.today()
    currtime = time(0,0)
    datetime_combined = datetime.combine(currtoday, currtime)
    userSquad = SquadMembers.query.filter_by(userID=current_user.id).first()
    if userSquad:
        squad = Squad.query.filter_by(id=userSquad.squadID).first()
        userSessions = Session.query.filter_by(date=datetime_combined, squadID=userSquad.squadID).all()
        squadName = squad.squadName
    else:
        userSessions = []
        squad = None
        squadName = ""
    selectedSession = None
    swimmerSession = None
    
    if request.method == 'POST':
        hydration = request.form.get('hydration')
        sleep = request.form.get('sleep')
        stress = request.form.get('stress')
        fatigue = request.form.get('fatigue')
        selectedSessionID = request.form.get('selectedSessionID')
        attendance = request.form.get('attendance')
        sessionGoals = request.form.get('sessionGoals')
        RAF = request.form.get('RAF') 
        journal = request.form.get('journal')
        journalPrivacy = request.form.get('journal')
        
        selectedSession = Session.query.filter_by(id=selectedSessionID).first()
        if selectedSession:
            session['selectedSessionID'] = selectedSession.id
        if sleep != None:
            print(sleep, stress, fatigue, hydration)
            ATT = 100*(0.1333*(10-int(stress))/10) + (0.1333*(10-int(fatigue))/10) + (0.1333*int(hydration)/5) + (int(sleep)/9)*0.6
            print(ATT)
            if attendance == "on":
                attendance = True
            else:
                attendance = False
            if ATT < 50.0:
                attendance = False
                absenceReason = "Ability to train below 50%." 
            
            if journalPrivacy == "on":
                journalPrivacy = "public"
            else:
                journalPrivacy = "private"

            selectedSessionID = session.get('selectedSessionID')
            selectedSession = Session.query.filter_by(id=selectedSessionID).first()
            if selectedSession:
                swimmerSession = SwimmerSession.query.filter_by(userID=current_user.id,sessionID=selectedSession.id)
                if swimmerSession:
                    swimmerSession.abilityToSwim = ATT
                    swimmerSession.attendance = attendance
                    swimmerSession.absenceReason = absenceReason
                    swimmerSession.RAF = int(RAF)
                    swimmerSession.sessionGoal = sessionGoals
                    swimmerSession.journal = journal
                    swimmerSession.journalPrivacy = journalPrivacy
                else:
                    newSwimmerSession = SwimmerSession(userID=current_user.id, sessionID=selectedSession.id,abilityToSwim=ATT, 
                                                attendance=attendance, absenceReason=absenceReason, RAF=int(RAF), 
                                                sessionGoal=sessionGoals, journal=journal, journalPrivacy=journalPrivacy)
                    db.session.add(newSwimmerSession)
                db.session.commit()
                if ATT < 50.0:
                    flash('Your calculated ability to train is less than recommended - do not attend training today.', category="success")
                else:
                    flash('Your details have been recorded!', category="success")
    return render_template("swimmerTodaySession.html", name=name, squadName=squadName, selectedSession=selectedSession, 
                           sessions=userSessions, swimmerSession=swimmerSession) 
   

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
    squadMember = SquadMembers.query.filter_by(userID=current_user.id).first() #query the datbase for a user with the provided id
    if squadMember:
        squadID = squadMember.squadID
    else:
        squadID = ""
    if request.method == 'POST':
        forename = request.form['forename']
        surname = request.form['surname']
        squads_id = request.form['squads_id']
        password1 = request.form['password1']
        password2 = request.form['password2']
        gender = request.form['gender']
        
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
        
        if gender != current_user.gender:
            current_user.gender = gender
        
        # If you want to update the password, handle it securely (e.g., hashing) before saving it.
        current_user.forename = forename #change forename
        current_user.surname = surname #change surname
        if len(password1) > 0: #if password is different
            current_user.password = generate_password_hash(password1, method='pbkdf2:sha256') #change password
        if squadID != "" and int(squads_id) != squadID: #if the squadID has changed
            currentsquad = SquadMembers.query.get(squadMember.id)
            db.session.delete(currentsquad)
            newSquadMember = SquadMembers(squadID=squads_id, userID=current_user.id) #create a new squad member
            db.session.add(newSquadMember)
        elif squadID == "" and int(squads_id) != squadID:
            newSquadMember = SquadMembers(squadID=squads_id, userID=current_user.id) #create a new squad member
            db.session.add(newSquadMember)

        db.session.commit() #save database
        flash('User information updated successfully.', 'success') #flash confirmation message
        return redirect(url_for('swimmerPages.swimmerSettings'))
    return render_template("swimmerSettings.html", user=current_user, squadID=squadID)

@login_required
@swimmerpages.route("/Goals", methods=["GET","POST"]) 
def swimmerGoals():
    today = date.today()
    year = today.year
    if request.method == 'POST': 
        seasonGoal = request.form.get('seasonGoal') #Gets the goal from the HTML 
        yearGoal = request.form.get('yearGoal') #Gets the goal from the HTML 
        longtermGoal = request.form.get('longtermGoal') #Gets the goal from the HTML 
        
        current_user.seasonGoal = seasonGoal
        current_user.yearlyGoal = yearGoal
        current_user.longtermGoal = longtermGoal
        db.session.commit()
        flash('Goals updated!', category='success')
            
    return render_template("swimmerGoals.html", user=current_user, year=year)

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