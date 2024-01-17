from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify #From the flask application, import Blueprint
from . import db
from .models import User, Session #, Event, Goals, Times
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required
import sqlite3
from random import randint
import json

swimmerpages = Blueprint("swimmerPages", __name__)

### Pages for the swimmers ###

@login_required
@swimmerpages.route("/Dashboard ") 
def swimmerDashboard():
    user = User.query.filter_by(id=current_user.id).first()
    if user:
        name=current_user.forename.capitalize()
    else:
        name=""
    return render_template("swimmerDashboard.html", name = name) 
   

@login_required
@swimmerpages.route("/Session", methods=['GET', 'POST']) 
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
    return render_template("swimmerSession.html", user=current_user)

@login_required
@swimmerpages.route("/Settings", methods=['GET', 'POST']) 
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
        current_user.squadID = squads_id
        if len(password1) > 0:
            current_user.password = generate_password_hash(password1, method='sha256')

        db.session.commit()
        flash('User information updated successfully', 'success')
        return redirect(url_for('swimmerPages.swimmerSettings'))
    return render_template("swimmerSettings.html", user=current_user)

# @login_required
# @swimmerpages.route("/Goals", methods=["GET","POST"]) 
# def swimmerGoals():
#     if request.method == 'POST': 
#         goal = request.form.get('goal') #Gets the goal from the HTML 
#         goaltype = request.form.get('goaltype')
        
#         if len(goal) < 1:
#             flash('Goal is too short!', category='error') 
#         else:
#             new_note = Goals(data=goal, user_id=current_user.id, goaltype=goaltype)  #providing the schema for the note 
#             db.session.add(new_note) #adding the note to the database 
#             db.session.commit()
#             flash('Goal added!', category='success')
#     return render_template("swimmerGoals.html", user=current_user)

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

# @login_required
# @swimmerpages.route("/PBs", methods={'GET','POST'}) 
# def swimmerPBs():
#     events = Event.query.all()
#     if request.method == 'POST': 
#         event = request.form.get('event')
#         competition = request.form.get('competition')
#         time = request.form.get('time')#Gets the goal from the HTML 
        
#         if len(event) < 1:
#             flash('Invalid entry!', category='error') 
#         else:
#             new_note = Times(event = event, time = time, competition = competition, user_id=current_user.id)  #providing the schema for the note 
#             db.session.add(new_note) #adding the note to the database 
#             db.session.commit()
#             flash('Time added!', category='success')
#     return render_template("swimmerPBs.html", user=current_user, events=events)

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
