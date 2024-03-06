#importing all the dependencies
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify #From the flask application, import Blueprint
from . import db
from .models import User, Exercise, Squad, SessionWorkout, SquadMembers #import the user, exercise and squad tables from the models page
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
@coachpages.route("/TodaySession")  
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachTodaySession():
    user = User.query.filter_by(id=current_user.id).first() #ensure that a user with the current user's id exists
    if user: #If the user exists
        name=current_user.forename.capitalize() #retrieve the forename of the current user
    else: #if the user doesn't exist
        name="" #pass in empty string
    return render_template("coachTodaySession.html", name=name) #render the coach dashboard template

#Route for the coach session page, supporting the post and get methods
@coachpages.route("/PreviousSessions", methods=['POST','GET'])
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachPreviousSessions():
    return render_template("coachPreviousSessions.html")


#Route for the coach workouts page, supporting the post and get methods
@coachpages.route("/Workouts", methods=['POST','GET']) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachWorkouts():
    exercises = Exercise.query.all()
    if request.method == 'POST': 
        #information from editing exercises
        newExercises = request.form.get('newExerciseName') #gets the new exercises from the form
        workoutName = request.form.get('name') #workout name retrieved from form
        ex1 = request.form.get('ex1') #gets the exercises from the form 
        rep1 = request.form.get('rep1') #gets the number of repetitions from the form
        ex2 = request.form.get('ex2') 
        rep2 = request.form.get('rep2') 
        ex3 = request.form.get('ex3') 
        rep3 = request.form.get('rep3') 
        ex4 = request.form.get('ex4') 
        rep4 = request.form.get('rep4')
        ex5 = request.form.get('ex5')
        rep5 = request.form.get('rep5')
        ex6 = request.form.get('ex6') 
        rep6 = request.form.get('rep6')
        ex7 = request.form.get('ex7') 
        rep7 = request.form.get('rep7')
        ex8 = request.form.get('ex8') 
        rep8 = request.form.get('rep8')
        ex9 = request.form.get('ex9') 
        rep9 = request.form.get('rep9') 
        ex10 = request.form.get('ex10')
        rep10 = request.form.get('rep10')
        
        #Adding a new exercise
        if newExercises != None:
            newExercises = newExercises.split(',') #extract the individual exercise names and store in a list
            for exercise in newExercises: #looping through new exercises
                exerciseExists = Exercise.query.filter_by(name=exercise).first()
                if not exerciseExists:
                    db.session.add(Exercise(name=exercise.strip())) #looping through exercises and storing stripped information
                    db.session.commit() #saving the database
                else:
                    newExercises.remove(exercise)
                    flash(f'{exercise} already added.', category='error')
            if len(newExercises) != 0:
                flash('Exercises added!', category='success')
        else: #if no new exercises will be added and a new workout will be made
            if workoutName: #if there is a workout name 
                if ex1 and rep1: #if the exercise and repetitions form aren't empty
                    ex = Exercise.query.filter_by(name=ex1).first() #then add the exercise to the workout
                    db.session.add(SessionWorkout(name=workoutName, reps=rep1, exerciseID=ex.ID, sessionID=1))
                if ex2 and rep2:
                    ex = Exercise.query.filter_by(name=ex2).first()
                    db.session.add(SessionWorkout(name=workoutName, reps=rep2, exerciseID=ex.ID, sessionID=1))
                if ex3 and rep3:
                    ex = Exercise.query.filter_by(name=ex3).first()
                    db.session.add(SessionWorkout(name=workoutName, reps=rep3, exerciseID=ex.ID, sessionID=1))
                if ex4 and rep4:
                    ex = Exercise.query.filter_by(name=ex4).first()
                    db.session.add(SessionWorkout(name=workoutName, reps=rep4, exerciseID=ex.ID, sessionID=1))
                if ex5 and rep5:
                    ex = Exercise.query.filter_by(name=ex5).first()
                    db.session.add(SessionWorkout(name=workoutName, reps=rep5, exerciseID=ex.ID, sessionID=1))
                if ex6 and rep6:
                    ex = Exercise.query.filter_by(name=ex6).first()
                    db.session.add(SessionWorkout(name=workoutName, reps=rep6, exerciseID=ex.ID, sessionID=1))
                if ex7 and rep7:
                    ex = Exercise.query.filter_by(name=ex7).first()
                    db.session.add(SessionWorkout(name=workoutName, reps=rep7, exerciseID=ex.ID, sessionID=1))
                if ex8 and rep8:
                    ex = Exercise.query.filter_by(name=ex8).first()
                    db.session.add(SessionWorkout(name=workoutName, reps=rep8, exerciseID=ex.ID, sessionID=1))
                if ex9 and rep9:
                    ex = Exercise.query.filter_by(name=ex9).first()
                    db.session.add(SessionWorkout(name=workoutName, reps=rep9, exerciseID=ex.ID, sessionID=1))
                if ex10 and rep10:
                    ex = Exercise.query.filter_by(name=ex10).first()
                    db.session.add(SessionWorkout(name=workoutName, reps=rep10, exerciseID=ex.ID, sessionID=1))
                db.session.commit() #save the database
        return redirect(url_for('coachPages.coachWorkout')) #refresh page
    
    #rendering the coach session page
    return render_template("coachWorkouts.html", user = current_user, exercises = exercises)

#Used to delete exercises
@coachpages.route('/delete-exercise', methods = ['POST'])
def delete_exercise():
    exercise = json.loads(request.data) #this function recieves a JSON from the index.js file
    exerciseID = exercise['exerciseID'] #retrieves the exerciseID to delete 
    exercise = Exercise.query.get(exerciseID) #queries the exercise
    if exercise: #if this exercise is found
        db.session.delete(exercise) #delete this exercise
        db.session.commit() #save the database
    return jsonify({}) #return empty input to index file

#route for the coach's my swimmers page, supporting get and post methods
@coachpages.route("/Squads", methods = {'GET', 'POST'}) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachSquads():
    squadMemberIDs = SquadMembers.query.filter_by(userID=current_user.id).all() #query the datbase for a user with the provided id
    if squadMemberIDs: #If the current user is part of a squad
        allMembers = []
        squads = []
        memberSquads = []
        for squadMemberID in squadMemberIDs:
            squad = Squad.query.filter_by(id=squadMemberID.squadID).first()
            squads.append(squad)
            members = SquadMembers.query.filter_by(squadID=squadMemberID.squadID).all()
            for member in members:
                allMembers.append(User.query.filter_by(id=member.userID).first())
            memberSquads.extend([squad.squadName]*len(members))
    else: #if there are no squads that the user is part of
        squads=[]
        members=[]
        memberSquads=[]
        
    if request.method == 'POST': #if there are inputs
        squadName = request.form.get('squadName') #retrieve the squadName from the page
        squadName_exists = Squad.query.filter_by(squadName=squadName).first() #Check if the squad name already exists
        
        if squadName_exists: #if it already exists
            flash("Squad name already in use.", category="error") #flash an error message
        elif len(squadName) < 2: #if the squadname is less than 2
            flash("Squad name too short.", category="error") #flash an error message
        else: 
            flash("Squad successfully created! Please refresh to update table.") #flash confirmation message
            squadCode = randint(1000,9999) #generate a random 4 digit squadCode
            new_squad = Squad(id=squadCode, squadName=squadName) #create a new squad
            db.session.add(new_squad) #add to database
            db.session.commit() #save the database

            #Add the current user into the squad
            userSquad = SquadMembers(squadID=squadCode, userID=current_user.id)
            db.session.add(userSquad)
            db.session.commit()
    return render_template("coachSquads.html", user=current_user, squads=squads, members=allMembers, memberSquads=memberSquads)


@coachpages.route("/Settings", methods=['GET', 'POST']) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachSettings(): 
    if request.method == 'POST': #when the method is post
        forename = request.form['forename'] #retrieve information from the form
        surname = request.form['surname']
        password1 = request.form['password1']
        password2 = request.form['password2']
        
        if len(forename) != 0 and len(forename) < 2: #if invalid forename entered
            flash('First name must be greater than 1 character.', category='error') #flash error message
        elif len(surname) != 0 and len(surname) < 2: #if invalid surname entered
            flash('Surname must be greater than 1 character.', category='error') #flash error message
        elif len(password1) != 0 and len(password1) < 8: #if invalid password entered
            flash('Password must be at least 8 char   acters.', category='error') #flash error message
        elif password1 != password2: #if passwords don't match
            flash('Passwords don\'t match.', category='error') #flash error message
        elif len(password1) != 0 and not isValid(password1): #if invalid password entered
            flash('Password must contain letters, numbers and special characters.', category='error') #flash error message
        
        # If you want to update the password, handle it securely (e.g., hashing) before saving it.
        if len(forename) > 0: #if forename is different
            current_user.forename = forename #change forename
        if len(surname) > 0: #if surname is different
            current_user.surname = surname #change surname
        if len(password1) > 0: #if password is different
            current_user.password = generate_password_hash(password1, method='pbkdf2:sha256') #change password

        db.session.commit() #save database
        flash('User information updated successfully.', 'success') #flash confirmation message
        return redirect(url_for('coachPages.coachSettings')) #refresh page
    return render_template("coachSettings.html", user=current_user) #render coach settings template

@coachpages.route("/Goals", methods=['GET', 'POST']) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachGoals(): 
    return render_template("coachGoals.html") #render coach goals template

@coachpages.route("/BaseTimes", methods=['GET', 'POST']) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachBaseTimes(): 
    return render_template("coachBaseTimes.html") #render coach base times template

@coachpages.route("/BestTimes", methods=['GET', 'POST']) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachBestTimes(): 
    return render_template("CoachBestTimes.html", user=current_user) #render coach best times template

@coachpages.route("/Competitions", methods=['GET', 'POST']) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachCompetitions(): 
    return render_template("coachCompetitions.html", user=current_user) #render coach goals template