from . import db #Import all from db, which is defined in the __init__.py file
from flask_login import UserMixin #User object will inherit from UserMixin
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy

class SessionWorkout(db.Model):
    __tablename__ = 'sessionworkout'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200)) #name of the workout
    sessionWorkoutExercises = db.relationship('SessionWorkoutExercises', backref="sessionworkout") #used for land training exercises
    workoutDescription = db.Column(db.String(3000)) #used for pool sessions
    session = db.relationship('SessionWorkoutsLink', backref="sessionworkout") #SessionID
    notes = db.Column(db.String(1000)) #notes on the workout
    workoutType = db.Column(db.String(50)) #land or pool

class SessionWorkoutExercises(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reps = db.Column(db.String(200)) #number of repetitions of the exercise
    exerciseID = db.Column(db.Integer, db.ForeignKey('exercise.id')) #exercise ID
    sessionWorkoutID = db.Column(db.Integer, db.ForeignKey('sessionworkout.name'))
    
class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200)) #name of exercise
    sessionWorkout = db.relationship('SessionWorkoutExercises',backref="exercise", passive_deletes=True) #relationship with sessionworkout table

class Squad(db.Model):
    __tablename__ = 'squad'
    id = db.Column(db.Integer, primary_key=True) 
    squadName = db.Column(db.String(150), unique=True) #name of squad
    squadMembers = db.relationship('SquadMembers', backref="squad") #a backref relationship with the session table
    session = db.relationship('Session', backref="squad") #backref relationship with session

class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column  (db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now) #default date is current date
    time = db.Column(db.String(150)) #AM/ PM
    squadID = db.Column(db.Integer, db.ForeignKey('squad.id')) #foreign key for squad
    swimmerSession = db.relationship('SwimmerSession', backref="session", passive_deletes=True) #backref relationship with SwimmerSession
    coachSession = db.relationship('CoachSession', backref="session")
    sessionWorkoutsLink = db.relationship('SessionWorkoutsLink', backref="session")
    
class SessionWorkoutsLink(db.Model):
    __tablename__ = 'sessionworkoutslink'
    id = db.Column(db.Integer, primary_key=True)
    sessionID = db.Column(db.Integer, db.ForeignKey('session.id'))
    sessionWorkoutID = db.Column(db.Integer, db.ForeignKey('sessionworkout.id'))
    
class User(db.Model, UserMixin): #Creating the user model
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True) #This userID is the primary key and unique to each user
    forename = db.Column(db.String(150)) #word
    surname = db.Column(db.String(150)) #word
    email = db.Column(db.String(150), unique=True) #unique=True ensures that no users have duplicate emails and usernames
    password = db.Column(db.String(150)) #string of characters
    seasonGoal = db.Column(db.String(1000)) #paragraph
    yearlyGoal = db.Column(db.String(1000)) #paragraph
    longtermGoal = db.Column(db.String(1000)) #paragraph
    role = db.Column(db.String(150)) #swimmer or coach
    SQquestion = db.Column(db.Integer) #security question 
    SQans = db.Column(db.String(150)) #security question answer
    squadMembers = db.relationship('SquadMembers', backref="user")
    competitionTimes = db.relationship('CompetitionTimes', backref="user")
    coachSession = db.relationship('CoachSession', backref="user")
    swimmerSession = db.relationship('SwimmerSession', backref="user")
    
class SquadMembers(db.Model):
    __tablename__ = 'squadmembers'
    id = db.Column(db.Integer, primary_key=True)
    squadID = db.Column(db.Integer, db.ForeignKey('squad.id'))
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))

class SwimmerSession(db.Model):
    __tablename__ = 'swimmersession'
    id = db.Column(db.Integer, primary_key=True)
    sessionID = db.Column(db.Integer, db.ForeignKey('session.id')) #foreign key for session
    attendance = db.Column(db.Boolean, default=False, nullable=False) #yes/no
    absenceReason = db.Column(db.String(500)) #paragraph
    sessionGoal = db.Column(db.String(1000)) #paragraph
    abilityToSwim = db.Column(db.Float) #percentage
    RAF = db.Column(db.Integer) #integer out of 10
    journalEntry = db.Column(db.String(1000)) #paragraph
    userID = db.Column(db.Integer, db.ForeignKey('user.id')) #foreign key for user

class CoachSession(db.Model):
    __tablename__ = 'coachsession'
    id = db.Column(db.Integer, primary_key=True)
    sessionID = db.Column(db.Integer, db.ForeignKey('session.id'))
    journalEntry = db.Column(db.String(1000))
    userID = db.Column(db.Integer, db.ForeignKey('user.id')) #foreign key for user

class CompetitionTimes(db.Model):
    __tablename__ = 'competitiontimes'
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id')) #foreign key for user
    timeSwam = db.Column(db.Float) #Time swam in seconds
    competitionID = db.Column(db.Integer, db.ForeignKey('competition.id')) #foreign key for competition
    finaPoints = db.Column(db.Integer) #FINA points scored from this swim
    splits = db.relationship('Split', backref="competitiontimes")
    eventID = db.Column(db.Integer, db.ForeignKey('event.id'))
    
class Competition(db.Model):
    __tablename__ = 'competition'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200)) #Competition name
    date = db.Column(db.DateTime(timezone=True), default=func.now()) #date of competition
    poolLength = db.Column(db.String(3)) #SCM, SCY, LCM
    competitionTimes = db.relationship('CompetitionTimes', backref="competition") 
    
class Split(db.Model):
    __tablename__ = 'split'
    id = db.Column(db.Integer, primary_key=True)
    competitionTimes = db.Column(db.Integer, db.ForeignKey('competitiontimes.id')) #foreign key for competitionrecord
    splitNum = db.Column(db.Integer) #the split number - 1 for first 50, etc. 
    splitTime = db.Column(db.Float) #the split time for that 50 and previous ones
    
class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(1)) #M or F
    stroke = db.Column(db.String(50)) #word
    poolDistance = db.Column(db.String(3)) #SCM, SCY, LCM
    distance = db.Column(db.String(50)) #100m, 200y, etc. 
    numOfSplits = db.Column(db.Integer) #number of split times expected for this event
    baseTime = db.Column(db.Float) #base time retrieved from world aquatics website - SCM
