from . import db #Import all from db
from flask_login import UserMixin
from sqlalchemy.sql import func
    
class SwimmerSession(db.Model):
    #sessionID
    #userID
    attendance = db.Column(db.Boolean, default=False, nullable=False)
    absenceReason = db.Column(db.String(500))
    sessionJournal = db.Column(db.String(1000))
    sessionGoal = db.Column(db.String(1000))
    stress = db.column(db.Integer)
    sleep = db.column(db.Integer)
    fatigue = db.column(db.Integer)
    urineColour = db.column(db.Integer)   

class SessionWorkout(db.Model):
    #exerciseID
    reps = db.Column(db.Integer)
    #sessionID

class Exercises(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    targetMuscles = db.Column(db.String(200))
    
    
class User(db.Model, UserMixin): #Creating the user model
    id = db.Column(db.Integer, primary_key=True) #This userID is the primary key and unique to each user
    forename = db.Column(db.String(150))
    surname = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True) #unique=True ensures that no users have duplicate emails and usernames
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now()) #The date and time when this is stored is saved as a new column
    squadID = db.Column(db.Integer)
    seasonGoal = db.Column(db.String(1000))
    yearlyGoal = db.Column(db.String(1000))
    gender = db.Column(db.String(150))
    birthday = db.Column(db.String(150))
    nationality = db.Column(db.String(150))
    formStroke = db.Column(db.String(150))

class Squads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    squadName = db.Column(db.String(150), unique=True)

class SquadCoaches(db.Model):
    ...
    #squadID
    #coachID

class CompetitionRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #userID
    timeSwam = db.Column(db.Float)
    #competitionID
    finaPoints = db.Column(db.Integer)
    
class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    poolLength = db.Column(db.String(3)) #SCM, SCY, LCM
    

class Splits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #CRID
    splitNum = db.Column(db.Integer)
    splitTime = db.Column(db.Integer)
    
class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stroke = db.Column(db.String(50))
    distance = db.Column(db.String(50))    ##### think about how you wanna do this