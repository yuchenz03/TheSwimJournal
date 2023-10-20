from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify #From the flask application, import Blueprint
from . import db
from .models import User
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required
import sqlite3
from random import randint
import json



pages = Blueprint("pages", __name__) #The blueprint name is now pages

#def get_db_connection():
    #swimJournal = sqlite3.connect('swimJournal.db')
    #swimJournal.row_factory = sqlite3.Row
    #return swimJournal
@pages.route("/conversionTool") 
def conversionTool():
    return render_template("conversionTool.html") #renders conversion tool template

@login_required
@pages.route("/coachDashboard")
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
@pages.route("/swimmerDashboard") 
def swimmerDashboard():
    user = User.query.filter_by(id=current_user.id).first()
    if user:
        name=current_user.forename.capitalize()
    else:
        name=""
    return render_template("swimmerDashboard.html", name = name) #, name = name
   


### Pages for the swimmers ###
@login_required
@pages.route("/swimmerSession", methods=['GET', 'POST']) 
def swimmerSession():
    if request.method == 'POST': 
        entry = request.form.get('entry')#Gets the entry from the HTML 
        
        if len(entry) < 1:
            flash('Entry is too short!', category='error') 
        else:
            new_entry = Journal(entry=entry, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_entry) #adding the note to the database 
            db.session.commit()
            flash('Entry added!', category='success')
    return render_template("swimmerSession.html", user=current_user)

@login_required
@pages.route("/swimmerSettings", methods=['GET', 'POST']) 
def swimmerSettings():
    if request.method == 'POST':
        forename = request.form['forename']
        surname = request.form['surname']
        squads_id = request.form['squads_id']
        password1 = request.form['password1']
        password2 = request.form['password2']
        
        if len(forename) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(surname) < 2:
            flash('Surname must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        
        # If you want to update the password, handle it securely (e.g., hashing) before saving it.
        current_user.forename = forename
        current_user.surname = surname
        current_user.squads_id = squads_id
        if len(password1) > 0:
            current_user.password = generate_password_hash(password1, method='sha256')

        db.session.commit()
        flash('User information updated successfully', 'success')
        return redirect(url_for('pages.swimmerSettings'))
    return render_template("swimmerSettings.html", user=current_user)

@login_required
@pages.route("/swimmerJournal", methods=["GET","POST"]) 
def swimmerJournal():
    if request.method == 'POST': 
        entry = request.form.get('entry')#Gets the entry from the HTML 
        
        if len(entry) < 1:
            flash('Entry is too short!', category='error') 
        else:
            new_entry = Journal(entry=entry, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_entry) #adding the note to the database 
            db.session.commit()
            flash('Entry added!', category='success')
            
    return render_template("swimmerJournal.html", user=current_user)

#Used to delete goals
@pages.route('/delete-entry', methods=['POST'])
def delete_entry():  
    entry = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    entryID = entry['entryID']
    entry = Journal.query.get(entryID)
    if entry:
        if entry.user_id == current_user.id:
            db.session.delete(entry)
            db.session.commit()

    return jsonify({})

@login_required
@pages.route("/swimmerAttendance") 
def swimmerAttendance():
    return render_template("swimmerAttendance.html")

@login_required
@pages.route("/swimmerGoals", methods=["GET","POST"]) 
def swimmerGoals():
    if request.method == 'POST': 
        goal = request.form.get('goal') #Gets the goal from the HTML 
        goaltype = request.form.get('goaltype')
        
        if len(goal) < 1:
            flash('Goal is too short!', category='error') 
        else:
            new_note = Goals(data=goal, user_id=current_user.id, goaltype=goaltype)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Goal added!', category='success')
    return render_template("swimmerGoals.html", user=current_user)

#Used to delete goals
@pages.route('/delete-goal', methods=['POST'])
def delete_goal():  
    goal = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    goalID = goal['goalID']
    goal = Goals.query.get(goalID)
    if goal:
        if goal.user_id == current_user.id:
            db.session.delete(goal)
            db.session.commit()

    return jsonify({})

@login_required
@pages.route("/swimmerPBs", methods={'GET','POST'}) 
def swimmerPBs():
    if request.method == 'POST': 
        event = request.form.get('event')
        competition = request.form.get('competition')
        time = request.form.get('time')#Gets the goal from the HTML 
        
        if len(event) < 1:
            flash('Invalid entry!', category='error') 
        else:
            new_note = Times(event = event, time = time, competition = competition, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Time added!', category='success')
    return render_template("swimmerPBs.html", user=current_user)

#Used to delete times
@pages.route('/delete-time', methods=['POST'])
def delete_time():  
    time = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    timeID = time['timeID']
    time = Times.query.get(timeID)
    if time:
        if time.user_id == current_user.id:
            db.session.delete(time)
            db.session.commit()

    return jsonify({})

### Pages for the Coaches ###
@login_required
@pages.route("/coachSession", methods=['POST','GET']) 
def coachSession():
    if request.method == 'POST': 
        exercisetype = request.form.get('exercisetype') #Gets the goal from the HTML 
        reps = request.form.get('reps')
        
        new_note = Exercise(name=exercisetype, user_id=current_user.id, reps=reps)  #providing the schema for the note 
        db.session.add(new_note) #adding the note to the database 
        db.session.commit()
        flash('Exercise added!', category='success')
    return render_template("coachSession.html", user = current_user)

#Used to delete goals
@pages.route('/delete-exercise', methods=['POST'])
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
@pages.route("/coachSwimmers", methods = {'GET', 'POST'}) 
def coachSwimmers():
    squad=""
    members=[]
    if request.method == 'POST': 
        squadName = request.form.get('squadName')
        squadName_exists = Squads.query.filter_by(squadName=squadName).first()
        
        if squadName_exists:
            flash("Squad name already in use.", category="error")
        elif len(squadName) < 2:
            flash("Squad name too short.", category="error")
        else:
            squadCode = randint(1000,9999)
            new_squad = Squads(id=squadCode, squadName=squadName, squadCode=squadCode)
            db.session.add(new_squad)
            db.session.commit()
    
        squad_id = squadCode
        current_user.squads_id = squad_id
        db.session.commit()
        squad = Squads.query.get(squad_id)
        if squad:
            members = User.query.filter_by(squads_id=squad_id).all()
            if squad is None:
                # Handle the case where the squad does not exist
                squad=[]
            if members is None:
                members=[]
            db.session.commit()
    return render_template("coachSwimmers.html", user=current_user, squad=squad,members=members)

@login_required
@pages.route("/coachJournal") 
def coachJournal():
    if request.method == 'POST': 
        entry = request.form.get('entry')#Gets the entry from the HTML 
        
        if len(entry) < 1:
            flash('Entry is too short!', category='error') 
        else:
            new_entry = Journal(entry=entry, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_entry) #adding the note to the database 
            db.session.commit()
            flash('Entry added!', category='success')
            
    return render_template("coachJournal.html", user=current_user)


@login_required
@pages.route("/coachSettings", methods=['GET', 'POST']) 
def coachSettings():
    if request.method == 'POST':
        forename = request.form['forename']
        surname = request.form['surname']
        password1 = request.form['password1']
        password2 = request.form['password2']
        
        if len(forename) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(surname) < 2:
            flash('Surname must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        
        # If you want to update the password, handle it securely (e.g., hashing) before saving it.
        current_user.forename = forename
        current_user.surname = surname
        if len(password1) > 0:
            current_user.password = generate_password_hash(password1, method='sha256')

        db.session.commit()
        flash('User information updated successfully', 'success')
        return redirect(url_for('pages.coachSettings'))
    return render_template("coachSettings.html", user=current_user)

@login_required
@pages.route("/coachAttendance") 
def coachAttendance():
    return render_template("coachAttendance.html")