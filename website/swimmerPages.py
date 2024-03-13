from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session #From the flask application, import Blueprint
from . import db
from .models import User, Session, SquadMembers, Squad, Event, SwimmerSession, Competition, CompetitionTimes
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required
import sqlite3
from random import randint
import json
from datetime import date, time, datetime, timedelta
import math

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
        journalPrivacy = request.form.get('journalPrivacy')
        
        absenceReason = None
        selectedSession = Session.query.filter_by(id=selectedSessionID).first()
        if selectedSession:
            session['selectedSessionID'] = selectedSession.id
        if sleep != None:
            ATT = 100*((0.1333*(10-int(stress))/10) + (0.1333*(10-int(fatigue))/10) + (0.1333*int(hydration)/5) + (int(sleep)/9)*0.6)
            ATT = math.trunc(ATT)
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
                
            if RAF == '':
                RAF = 0

            selectedSessionID = session.get('selectedSessionID')
            selectedSession = Session.query.filter_by(id=selectedSessionID).first()
            if selectedSession:
                swimmerSession = SwimmerSession.query.filter_by(userID=current_user.id,sessionID=selectedSession.id).first()
                if swimmerSession:
                    swimmerSession.abilityToSwim = ATT
                    swimmerSession.attendance = attendance
                    swimmerSession.absenceReason = absenceReason
                    swimmerSession.RAF = int(RAF)
                    swimmerSession.sessionGoal = sessionGoals
                    swimmerSession.journalEntry = journal
                    swimmerSession.journalPrivacy = journalPrivacy
                    db.session.commit()
                else:
                    newSwimmerSession = SwimmerSession(userID=current_user.id, sessionID=selectedSession.id,abilityToSwim=ATT, 
                                                attendance=attendance, absenceReason=absenceReason, RAF=int(RAF), 
                                                sessionGoal=sessionGoals, journalEntry=journal, journalPrivacy=journalPrivacy)
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
    attendedSessions = SwimmerSession.query.filter_by(userID=current_user.id).all()
    selectedSession = None
    datetoday = date.today() + timedelta(0)
    dateweek = datetoday - timedelta(7)
    allSessions = []
    weekSessions = SwimmerSession.query.filter(SwimmerSession.dateCreated.between(dateweek, datetoday+timedelta(1))).all()
    print(weekSessions)
    ATSsum = 0
    RAFsum = 0
    averageATS = 0
    averageRAF = 0
    sessionNum = len(weekSessions)
    if sessionNum > 0:
        for _session in weekSessions:
            ATSsum += _session.abilityToSwim
            RAFsum += _session.RAF
        averageATS = ATSsum // sessionNum
        averageRAF = RAFsum // sessionNum
    
    for _session in attendedSessions:
        allSessions.append(Session.query.filter_by(id=_session.sessionID).first())
    
    if request.method == "POST":
        selectedSessionID = request.form.get('selectedSessionID')
        selectedSession = SwimmerSession.query.filter_by(sessionID=selectedSessionID, userID=current_user.id).first()
        if not selectedSession:
            flash("Invalid session", category="error")
    return render_template("swimmerPreviousSessions.html", selectedSession=selectedSession, allSessions=allSessions,
                           sessionNum=sessionNum, averageATS=averageATS, averageRAF=averageRAF, datetoday=datetoday, dateweek=dateweek)

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
    allCompetitions = Competition.query.all()
    selectedCompetition = None
    allEvents = []
    eventNum = 0
    chosenCompEvents = []
    chosenCompTimes = []
    if request.method == "POST":
        compName = request.form.get("compName")
        compDate = request.form.get("compDate")
        poolLength = request.form.get("poolLength")
        eventNum = request.form.get("eventNum")
        selectedCompetitionID = request.form.get("selectedCompetitionID")
        compEvents = request.form.getlist("events[]")
        compTimes = request.form.getlist("times[]")
        
        if eventNum == None:
            eventNum = 0
        
        if compDate != None: #If a date of competition is to be entered
            if compDate == '':
                flash('Please enter a competition date.', category="error")
                return redirect(url_for('swimmerPages.swimmerCompetitions'))
            dateFormat = "%Y-%m-%d" 
            dateObject = datetime.strptime(compDate, dateFormat)+timedelta(0)
        
            compexists = Competition.query.filter_by(name=compName,date=dateObject,poolLength=poolLength).first()
            if compexists:
                flash('Competition already exists!', category="error")
                return redirect(url_for('swimmerPages.swimmerCompetitions'))
            if len(compName) < 2:
                flash('Please enter a valid competition name.', category="error")
            elif poolLength == "":
                flash('Please enter a pool length.', category="error")
            elif eventNum == None:
                flash('Please choose a number of events.', category="error")
            else:
                newComp = Competition(name=compName, date=dateObject, poolLength=poolLength)
                db.session.add(newComp)
                db.session.commit()
                currentCompetition = Competition.query.filter_by(name=compName, date=dateObject, poolLength=poolLength).first()
                session['currentCompID'] = currentCompetition.id
                session['eventNum'] = eventNum
                allEvents = Event.query.filter_by(gender=current_user.gender,poolDistance=currentCompetition.poolLength).all()
                flash("Competition created!", category="success")
            
        if compEvents != []:
            eventNum = session.get('eventNum')
            if len(compEvents) != int(eventNum) or "" in compEvents:
                flash("Please choose events for all selections.",category="success")
            else:
                currentCompID = session.get('currentCompID')
                currentCompetition = Competition.query.filter_by(id=currentCompID).first()
                for i in range(len(compEvents)):
                    compEvent = Event.query.filter_by(id=compEvents[i]).first()
                    baseTime = compEvent.baseTime
                    points = math.trunc(1000*(baseTime/float(compTimes[i]))**3)
                    db.session.add(CompetitionTimes(finaPoints=points,timeSwam=compTimes[i],userID=current_user.id,competitionID=currentCompetition.id,eventID=compEvents[i]))
                db.session.commit()
                eventNum = 0
                flash("Events entered!", category="success")
                
        if selectedCompetitionID:
            selectedCompetition = Competition.query.filter_by(id=selectedCompetitionID).first()
            chosenCompTimes = CompetitionTimes.query.filter_by(competitionID=selectedCompetitionID,userID=current_user.id).all()
            for time in chosenCompTimes:
                chosenCompEvents.append(Event.query.filter_by(id=time.eventID).first())
            
    return render_template("swimmerCompetitions.html", allCompetitions=allCompetitions, selectedCompetition=selectedCompetition,
                           allEvents=allEvents, eventNum=int(eventNum), chosenCompEvents=chosenCompEvents,chosenCompTimes=chosenCompTimes)

@login_required
@swimmerpages.route("/Progression", methods={'GET', 'POST'})
def swimmerProgression():
    allEvents = Event.query.filter_by(gender=current_user.gender)
    progressionType = None
    bestTimes = []
    eventNames = []
    eventTimes = []
    eventComp = []
    eventDate = []
    timesSwam = []
    timeComp = []
    timeDate = []
    labels = []
    values = []
    chosenEventInstance = None
    if request.method == "POST":
        tableType = request.form.get("tableType")
        chosenEvent = request.form.get("chosenEvent")
        if tableType == "":
            flash("Please choose a type of progression to display.",category="error")
        else:
            progressionType = tableType
            eventIDs = []
            eventNames = []
            eventTimes = []
            eventComp = []
            eventDate = []
            if tableType == "bestTimes":
                allTimes = CompetitionTimes.query.filter_by(userID=current_user.id).all()
                for time in allTimes:
                    if time.eventID not in eventIDs:
                        eventIDs.append(time.eventID)
                        event = Event.query.filter_by(id=time.eventID).first()
                        eventNames.append(f"{event.distance} {event.stroke} {event.poolDistance}")
                        eventTimes.append(time.timeSwam)
                        eventCompetition = Competition.query.filter_by(id=time.competitionID).first()
                        eventComp.append(eventCompetition.name)
                        EDate = str(eventCompetition.date)
                        eventDate.append(EDate.replace("00:00:00",""))
                    else: #if the event has already been found
                        indexpos = eventIDs.index(time.eventID)
                        if eventTimes[indexpos] > time.timeSwam:
                            eventTimes[indexpos] = time.timeSwam
                            eventCompetition = Competition.query.filter_by(id=time.competitionID).first()
                            eventComp[indexpos] = eventCompetition.name
                            EDate = str(eventCompetition.date)
                            eventDate[indexpos] = EDate.replace("00:00:00","")
            elif tableType == "eventHistory":
                session["tableType"] = "eventHistory"
            if chosenEvent:
                if chosenEvent == "":
                    flash("Please choose an event to view event history for.", category="error")
                else:
                    graphData = []
                    timesSwam = []
                    timeComp = []
                    timeDate = []
                    chosenEventInstance = Event.query.filter_by(id=chosenEvent).first()
                    compTimesInstances = CompetitionTimes.query.filter_by(eventID=chosenEventInstance.id).all()
                    for time in compTimesInstances:
                        timesSwam.append(time.timeSwam)
                        timeCompetition = Competition.query.filter_by(id=time.competitionID).first()
                        timeComp.append(timeCompetition.name)
                        EDate = str(timeCompetition.date)
                        timeDate.append(EDate.replace("00:00:00",""))
                        graphData.append((EDate.replace("00:00:00",""),time.timeSwam))
                        labels = [row[0] for row in graphData]
                        values = [row[1] for row in graphData]
            
                        
    return render_template("swimmerProgression.html", bestTimes=bestTimes,progressionType=progressionType, eventTimes=eventTimes,
                           eventComp=eventComp,eventNames=eventNames,eventDate=eventDate,allEvents=allEvents,
                           chosenEventInstance=chosenEventInstance, timesSwam=timesSwam, timeComp=timeComp,timeDate=timeDate,
                           labels=labels,values=values)