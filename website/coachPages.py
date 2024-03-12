#importing all the dependencies
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session #From the flask application, import Blueprint
from . import db
from .models import User, Event, Exercise, Squad, Session, SessionWorkoutExercises, SessionWorkout, SquadMembers #import the user, exercise and squad tables from the models page
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required
from random import randint
import json
from datetime import date, time, timedelta, datetime

#define a new blueprint named coachPages
coachpages = Blueprint("coachPages", __name__)

### Pages for the Coaches ###

#Function to check if a password is valid
def isValid(password):
    letter = any(c.isalpha() for c in password)
    digit = any(c.isdigit() for c in password)
    specialChar = any(not c.isalnum() for c in password)

    return letter and digit and specialChar 

#Function that returns the date of the previous monday
def findLastMonday(currdate):
    daysAhead = currdate.weekday()
    return currdate - timedelta(days=daysAhead)


#Route for the coach's dashboard page
@coachpages.route("/TodaySession", methods=['POST', 'GET'])  
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachTodaySession():
    swimmers = []
    user = User.query.filter_by(id=current_user.id).first() #ensure that a user with the current user's id exists
    if user: #If the user exists
        name=current_user.forename.capitalize() #retrieve the forename of the current user
    else: #if the user doesn't exist
        name="" #pass in empty string
    currtoday = date.today()
    currtime = time(0,0)
    datetime_combined = datetime.combine(currtoday, currtime)
    todaySessions = Session.query.filter_by(date=datetime_combined).all()
    userSquads = SquadMembers.query.filter_by(userID=current_user.id).all()
    userSquadIDs = []
    for squad in userSquads:
        userSquadIDs.append(squad.squadID)
    for session in todaySessions:
        if session.squadID not in userSquadIDs:
            todaySessions.remove(session)
    sessionSquad = []
    for session in todaySessions:
        squad = Squad.query.filter_by(id=session.squadID).first()
        sessionSquad.append(squad.squadName)
    
    if request.method == 'POST':
        selectedSessionID = request.form.get('selectedSessionID')
        if selectedSessionID == "":
            flash('Please choose a session.', category="error")
        else:
            selectedSession = Session.query.filter_by(id=int(selectedSessionID)).first()
            if not selectedSession:
                flash('Session does not exist.', category="error")
                return redirect(url_for('coachPages.coachTodaySession')) #refresh page
            swimmers = []
            sessionSquad = Squad.query.filter_by(id=selectedSession.squadID).first()
            members = SquadMembers.query.filter_by(squadID=sessionSquad.id).all()
            for member in members:
                userinstance = User.query.filter_by(id=member.userID).first()
                if userinstance.role == "Swimmer":
                    swimmers.append(userinstance)
                
    return render_template("coachTodaySession.html", name=name, todaySessions=todaySessions, sessionSquad=sessionSquad,
                           swimmers=swimmers) #render the coach dashboard template

@coachpages.route("/Timetables", methods=['POST', 'GET'])
@login_required 
def coachTimetables():
    squads = []
    coachSquads = SquadMembers.query.filter_by(userID=current_user.id).all() #retrieving all the coach's squads from the database
    today = date.today() #finding today's date
    for squad in coachSquads:
        squads.append(Squad.query.filter_by(id=squad.squadID).first()) #finding the instance of the squads.
    if request.method == 'POST':
        chosenSquad = request.form.get('chosenSquad')
        mondayAM = request.form.get('mondayAM') #Getting the starting times for each of possible sessions
        mondayPM = request.form.get('mondayPM') 
        tuesdayAM = request.form.get('tuesdayAM')
        tuesdayPM = request.form.get('tuesdayPM')
        wednesdayAM = request.form.get('wednesdayAM')
        wednesdayPM = request.form.get('wednesdayPM')
        thursdayAM = request.form.get('thursdayAM')
        thursdayPM = request.form.get('thursdayPM')
        fridayAM = request.form.get('fridayAM')
        fridayPM = request.form.get('fridayPM')
        saturdayAM = request.form.get('saturdayAM')
        saturdayPM = request.form.get('saturdayPM')
        sundayAM = request.form.get('sundayAM')
        sundayPM = request.form.get('sundayPM')

        
        userInputs = [mondayAM, mondayPM, tuesdayAM, tuesdayPM, wednesdayAM, wednesdayPM, 
                      thursdayAM, thursdayPM, fridayAM, fridayPM, saturdayAM, saturdayPM, 
                      sundayAM, sundayPM]
        if chosenSquad == "":
            flash('Please assign the timetable to a squad.', category="error")
        else:
            #checking if an old timetable exists, and deleting it
            oldSessions = Session.query.filter_by(squadID=chosenSquad).all()
            if oldSessions:
                for session in oldSessions:
                    sessionToDelete = Session.query.get(session.id)
                    db.session.delete(sessionToDelete)
            #inputting the new timetable in
            start = findLastMonday(today)
            for i in range(len(userInputs)):
                if userInputs[i] == "on":
                    startday = start + timedelta(days=i//2)
                    if i%2 == 0:
                        time = "AM"
                    else:
                        time = "PM"
                    for j in range(52):
                        sessionday = startday + timedelta(7*j)
                        newSession = Session(date=sessionday, time=time, squadID=chosenSquad)
                        db.session.add(newSession)
            db.session.commit()
            flash('Timetable added!', category="success")
        
    return render_template("coachTimetable.html", squads=squads)

#Route for the coach session page, supporting the post and get methods
@coachpages.route("/PreviousSessions", methods=['POST','GET'])
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachPreviousSessions():
    return render_template("coachPreviousSessions.html")


@coachpages.route("/Exercises", methods=['POST','GET'])
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachExercises():
    exercises = Exercise.query.all()
    if request.method == 'POST':
        newExercise = request.form.get('newExerciseName') #gets the new exercises from the form
        #Adding a new exercise
        if newExercise != None:
            exerciseExists = Exercise.query.filter_by(name=newExercise).first()
            if not exerciseExists:
                db.session.add(Exercise(name=newExercise.strip().capitalize())) #stripping values before storing them
                db.session.commit() #saving the database
                flash('Exercises added!', category='success')
                return redirect(url_for('coachPages.coachExercises')) #refresh page
            else:
                flash(f'{newExercise} already added.', category='error')
                
    return render_template("coachExercises.html", exercises=exercises)


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

#Route for the coach workouts page, supporting the post and get methods
@coachpages.route("/Workouts", methods=['POST','GET']) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachWorkouts():
    existingWorkouts = SessionWorkout.query.all() #Retrieving all existingWorkouts
    viewWorkout = None #Initializing viewWorkout, workoutExercises, exerciseNames and exerciseReps
    workoutExercises = None
    exerciseNames = None
    exerciseReps = None
    exercises = None
    allExercises = Exercise.query.all() 
    if request.method == 'POST': 
        workoutName = request.form.get('name') #Information retrieved from form
        workoutExercises = request.form.get('workoutExercises') 
        workoutNotes = request.form.get('workoutNotes')
        workoutType = request.form.get('workoutType')
        viewWorkoutID = request.form.get('viewWorkoutID')
        newExerciseReps = request.form.get('newExerciseReps')
        newExerciseID = request.form.get('newExerciseID')
        notes = request.form.get('notes')
        newWorkoutDescription = request.form.get("newWorkoutDescription")
        
        if workoutName: #If a workout is to be created
            workoutExists = SessionWorkout.query.filter_by(name=workoutName).first() 
            if not workoutExists: #If the workout name is not already in use:
                if workoutType == 'land': #For land workouts, create a workout first
                    db.session.add(SessionWorkout(name=workoutName, notes=workoutNotes, workoutType=workoutType, workoutDescription=workoutExercises))
                    db.session.commit() #saving the database
                    #Saving the workout exercises entered by the user
                    if workoutExercises: #If there are workout exercises:
                        currentworkout = SessionWorkout.query.filter_by(name=workoutName).first()
                        workoutExercises = workoutExercises.split('\r\n') #extract the individual exercise names and reps and store in a list
                        print(workoutExercises)
                        for workoutExercise in workoutExercises: #looping through exercises
                            workoutExercise = workoutExercise.split(",") #Split into exercise and reps
                            exercise = workoutExercise[0].strip() #extract exercise
                            exercise = exercise.capitalize() #capitalize the exercise to fit format in database
                            exerciseObject = Exercise.query.filter_by(name=exercise).first() #find the exercise in database
                            if exerciseObject: #if the exercise exists in database
                                try: 
                                    repetitions = int(workoutExercise[1].strip()) 
                                except ValueError: #Ensuring the number of repetitions is an integer
                                    flash('Please enter repetitions as an integer.', category='error')
                                #If all conditions are met, create the exercises
                                db.session.add(SessionWorkoutExercises(reps=repetitions,exerciseID=exerciseObject.id,sessionWorkoutID=currentworkout.id))
                                db.session.commit() #saving the database
                            else: #if the exercise doesn't exist
                                flash('Exercise does not exist in database.', category='error')
                                #flash an error message, delete the previously created workout
                                workout = SessionWorkout.query.get(currentworkout.id)
                                db.session.delete(workout)
                                db.session.commit()
                                return redirect(url_for('coachPages.coachWorkouts')) #refresh page
                        flash('Workout Created!', category='success')
                        return redirect(url_for('coachPages.coachWorkouts')) #refresh page
                    #if no workout exercises are entered
                    else:
                        flash('Please enter at least one exercise.', category='error')
                        workout = SessionWorkout.query.get(currentworkout.id)
                        db.session.delete(workout)
                        db.session.commit()
                #for swim workouts
                else:
                    db.session.add(SessionWorkout(name=workoutName, notes=workoutNotes, workoutType=workoutType, workoutDescription=workoutExercises))
                    db.session.commit() #saving the database
                    flash('Workout Created!', category='success')
                    return redirect(url_for('coachPages.coachWorkouts')) #refresh page
            #if workout with the name already exists
            else:
                flash('Workout name already in use.', category='error')
        #If there is no workout name but there is workoutExercises and workoutNotes
        if (workoutExercises!=None or workoutNotes!=None) and len(workoutName)==0:
            flash('Cannot create workout without name.', category='error')
        #If no workout is chosen to be viewed
        if viewWorkoutID == None:
            viewWorkout = None
        #If a workout has been chosen to be viewed
        else:
            exercises = []
            exerciseNames = []
            exerciseReps = []
            #find workout to be viewed within the database  
            viewWorkout = SessionWorkout.query.filter_by(id=viewWorkoutID).first()
            session['viewWorkoutID'] = viewWorkout.id #add the current workout to the session
            #if the type of workout is land
            if viewWorkout.workoutType == "land":
                #retrieve the exercises within the workout by querying the SessionWorkoutExercises table
                workoutExercises = SessionWorkoutExercises.query.filter_by(sessionWorkoutID=viewWorkoutID).all()
                #For each workout exercise
                for workoutExercise in workoutExercises:
                    currexercise = Exercise.query.filter_by(id=workoutExercise.exerciseID).first()
                    #add the exercise object into the exercises list
                    exercises.append(currexercise)
                    #add the reps into the corresponding list
                    exerciseReps.append(workoutExercise.reps)
                for exercise in exercises:
                    #For each exercise, append its name into the list.
                    exerciseNames.append(exercise.name)
        notesChanged = False 
        viewWorkoutID = session.get('viewWorkoutID') #retrieving the current workout from session
        currworkout = SessionWorkout.query.filter_by(id=viewWorkoutID).first() 
        if notes and newWorkoutDescription: #the if statements are to avoid the error where 
            #nested flashes occur
            if currworkout.notes != notes: #if notes have changed, then 
                #change the current workout's notes
                currworkout.notes = notes
            if currworkout.workoutDescription != newWorkoutDescription: 
                #if the workout description has changed, then change it
                currworkout.workoutDescription = newWorkoutDescription
            db.session.commit()
            if not (currworkout.notes == notes and currworkout.workoutDescription == newWorkoutDescription):
                flash('Edits saved!', category='success')
        elif notes:
            if currworkout.notes != notes:
                notesChanged = True
                currworkout.notes = notes
                db.session.commit()
                flash('Edits saved!', category='success')
        elif newWorkoutDescription:
            if currworkout.workoutDescription != newWorkoutDescription:
                currworkout.workoutDescription = newWorkoutDescription
                db.session.commit()
                flash('Edits saved!', category='success')
        #if a new exercise is to be created, check if all information required is present.
        if newExerciseID and newExerciseReps:
            newExercise = SessionWorkoutExercises(reps=newExerciseReps, exerciseID=newExerciseID, sessionWorkoutID=viewWorkoutID)
            db.session.add(newExercise)
            db.session.commit()
            if notesChanged == False: #to avoid nested flashes, check if a flash
                #has already occured in changing the notes.
                flash('Edits saved!', category='success')
            return redirect(url_for('coachPages.coachWorkouts')) #refresh page
        #If only the reps have been entered, or only the exercise is entered,
        #flash error messages
        elif newExerciseReps and not newExerciseID:
            flash('Please choose an exercise.', category='error')
            return redirect(url_for('coachPages.coachWorkouts')) #refresh page
        elif newExerciseID and not newExerciseReps:
            flash('Please enter the number of repetitions.', category='error')
            return redirect(url_for('coachPages.coachWorkouts')) #refresh page
    #rendering the coach session page
    return render_template("coachWorkouts.html", user=current_user, allExercises=allExercises, workoutExercises=workoutExercises, 
                           exercises=exercises, existingWorkouts=existingWorkouts, workout=viewWorkout, exerciseNames=exerciseNames, 
                           exerciseReps=exerciseReps)

#Used to delete workout exercises
@coachpages.route('/delete-workout-exercise', methods = ['POST'])
def delete_workout_exercise():
    workoutExercise = json.loads(request.data) #this function recieves a JSON from the index.js file
    workoutExerciseID = workoutExercise['workoutExerciseID'] #retrieves the exerciseID to delete 
    workoutExercise = SessionWorkoutExercises.query.get(workoutExerciseID) #queries the exercise
    if workoutExercise: #if this exercise is found
        db.session.delete(workoutExercise) #delete this exercise
        db.session.commit() #save the database
        flash('Exercise successfully deleted.', category="success")
    return jsonify({}) #return empty input to index file

#route for the coach's quads page, supporting get and post methods
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
        allMembers=[]
        memberSquads=[]
        
    if request.method == 'POST': #if there are inputs
        squadName = request.form.get('squadName') #retrieve the squadName from the page
        squadName_exists = Squad.query.filter_by(squadName=squadName).first() #Check if the squad name already exists
        
        if squadName_exists: #if it already exists
            flash("Squad name already in use.", category="error") #flash an error message
        elif len(squadName) < 2: #if the squadname is less than 2
            flash("Squad name too short.", category="error") #flash an error message
        else: 
            flash("Squad successfully created! ") #flash confirmation message
            squadCode = randint(1000,9999) #generate a random 4 digit squadCode
            new_squad = Squad(id=squadCode, squadName=squadName) #create a new squad
            db.session.add(new_squad) #add to database
            db.session.commit() #save the database

            #Add the current user into the squad
            userSquad = SquadMembers(squadID=squadCode, userID=current_user.id)
            db.session.add(userSquad)
            db.session.commit()
            return redirect(url_for('coachPages.coachSquads')) #refresh page
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
    today = date.today()
    year = today.year
    squadMemberIDs = SquadMembers.query.filter_by(userID=current_user.id).all() #query the datbase for a user with the provided id
    if squadMemberIDs: #If the current user is part of a squad
        allMembers = []
        squads = []
        for squadMemberID in squadMemberIDs:
            squad = Squad.query.filter_by(id=squadMemberID.squadID).first()
            squads.append(squad)
            members = SquadMembers.query.filter_by(squadID=squadMemberID.squadID).all()
            for member in members:
                chosenuser = User.query.filter_by(id=member.userID).first()
                if chosenuser.role == "Swimmer": 
                    allMembers.append(chosenuser)
    else:
        allMembers = []
    return render_template("coachGoals.html", members=allMembers, year=year) #render coach goals template

@coachpages.route("/BaseTimes", methods=['GET', 'POST']) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachBaseTimes(): 
    events = Event.query.all()
    if request.method == 'POST':
        gender = request.form.get('gender')
        poolDistance = request.form.get('poolDistance')
        stroke = request.form.get('stroke')
        distance = request.form.get('distance')
        timeM = request.form.get('timeM')
        timeS = request.form.get('timeS')
        timeMS = request.form.get('timeMS')
        
        if timeM == '' or timeS == '' or timeMS == '':
            flash('Please enter a time.', category='error')
            return redirect(url_for('coachPages.coachBaseTimes'))
        else:
            timeM = int(timeM)
            timeS = int(timeS)
            timeMS = int(timeMS)
        
        chosenEvent = Event.query.filter_by(gender=gender,poolDistance=poolDistance,
                                            stroke=stroke,distance=distance).first()
        if chosenEvent:
            basetime = timeM*60+timeS+timeMS/100
            chosenEvent.baseTime = basetime
            db.session.commit()
            flash('Time entered!', category="success")
        else:
            flash('Please enter a valid event', category="error")

    return render_template("coachBaseTimes.html", events=events) #render coach base times template

@coachpages.route("/BestTimes", methods=['GET', 'POST']) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachBestTimes(): 
    return render_template("CoachBestTimes.html", user=current_user) #render coach best times template

@coachpages.route("/Competitions", methods=['GET', 'POST']) 
@login_required #decorator to ensure only authenticated users can access this page, otherwise they are redirected to the login page
def coachCompetitions(): 
    return render_template("coachCompetitions.html", user=current_user) #render coach goals template