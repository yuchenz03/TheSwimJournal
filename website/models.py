from . import db #Import all from db, which is defined in the __init__.py file
from flask_login import UserMixin #User object will inherit from UserMixin
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
    
class SwimmerSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sessionID = db.Column(db.Integer, db.ForeignKey('session.id')) #foreign key for session
    attendance = db.Column(db.Boolean, default=False, nullable=False) #yes/no
    absenceReason = db.Column(db.String(500)) #paragraph
    sessionGoal = db.Column(db.String(1000)) #paragraph
    stress = db.Column(db.Integer) #1-10
    sleep = db.Column(db.Integer) #0-12
    fatigue = db.Column(db.Integer) #1-10
    urineColour = db.Column(db.Integer) #1-5 1 being light yellow, 5 being orange

class SessionWorkout(db.Model):
    name = db.Column(db.String(200), primary_key=True) #name of the workout
    reps = db.Column(db.String(200)) #number of repetitions of the exercise
    exerciseID = db.Column(db.Integer, db.ForeignKey('exercise.id'), primary_key=True) #exercise ID
    sessionID = db.Column(db.Integer, db.ForeignKey('session.id')) #SessionID

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200)) #name of exercise
    sessionWorkout = db.relationship('SessionWorkout') #relationship with sessionworkout table

class Squad(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    squadName = db.Column(db.String(150), unique=True) #name of squad
    user = db.relationship('User', backref="squad") #a backref relationship with the session table
    squadCoaches = db.relationship('SquadCoach', backref="squad") #backref relationship with coaches of the squad
    session = db.relationship('Session', backref="squad") #backref relationship with session

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now) #default date is current date
    time = db.Column(db.String(150)) #AM/ PM
    journal = db.Column(db.String(1000)) #paragraph
    squadID = db.Column(db.Integer, db.ForeignKey('squad.id')) #foreign key for squad
    userID = db.Column(db.Integer, db.ForeignKey('user.id')) #foreign key for user
    swimmerSession = db.relationship('SwimmerSession', backref="session", passive_deletes=True) #backref relationship with SwimmerSession
    sessionWorkout = db.relationship('SessionWorkout', backref="sessionworkout")
    
class User(db.Model, UserMixin): #Creating the user model
    id = db.Column(db.Integer, primary_key=True) #This userID is the primary key and unique to each user
    forename = db.Column(db.String(150)) #word
    surname = db.Column(db.String(150)) #word
    email = db.Column(db.String(150), unique=True) #unique=True ensures that no users have duplicate emails and usernames
    password = db.Column(db.String(150)) #string of characters
    date_created = db.Column(db.DateTime(timezone=True), default=func.now()) #The date and time when this is stored is saved as a new column
    squadID = db.Column(db.Integer, db.ForeignKey('squad.id')) #foreign key for squad
    seasonGoal = db.Column(db.String(1000)) #paragraph
    yearlyGoal = db.Column(db.String(1000)) #paragraph
    gender = db.Column(db.String(6)) #Male or Female
    birthday = db.Column(db.Date) #yyyy-mm-dd
    nationality = db.Column(db.String(150)) #preset values
    formStroke = db.Column(db.String(150)) #preset values
    session = db.relationship('Session', backref="user", passive_deletes=True) #a backref relationship with the session table
    squadCoaches = db.relationship('SquadCoach', backref="user") #a backref relationship with the squadCoaches table
    competitionRecord = db.relationship('Competitionrecord', backref="user")
    role = db.Column(db.String(150)) #swimmer 
    SQquestion = db.Column(db.Integer) #security question number
    SQans = db.Column(db.String(150)) #security question answer

class SquadCoach(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    squadID = db.Column(db.Integer, db.ForeignKey('squad.id')) #foreign key for squad
    coachID = db.Column(db.Integer, db.ForeignKey('user.id'))

class Competitionrecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id')) #foreign key for user
    timeSwam = db.Column(db.Float) #Time swam in seconds
    competitionID = db.Column(db.Integer, db.ForeignKey('competition.id')) #foreign key for competition
    finaPoints = db.Column(db.Integer) #FINA points scored from this swim
    splits = db.relationship('Split', backref="competitionrecord")
    eventID = db.Column(db.Integer, db.ForeignKey('event.id'))
    
class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200)) #Competition name
    date = db.Column(db.DateTime(timezone=True), default=func.now()) #date of competition
    poolLength = db.Column(db.String(3)) #SCM, SCY, LCM
    competitionRecord = db.relationship('Competitionrecord', backref="competition") 
    
class Split(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competitionRecord = db.Column(db.Integer, db.ForeignKey('competitionrecord.id')) #foreign key for competitionrecord
    splitNum = db.Column(db.Integer) #the split number - 1 for first 50, etc. 
    splitTime = db.Column(db.Float) #the split time for that 50 and previous ones
    
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(1)) #M or F
    stroke = db.Column(db.String(50)) #word
    poolDistance = db.Column(db.String(3)) #SCM, SCY, LCM
    distance = db.Column(db.String(50)) #100m, 200y, etc. 
    baseTime = db.Column(db.Float) #base time retrieved from world aquatics website - SCM
