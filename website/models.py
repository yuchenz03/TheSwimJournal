from . import db #Import all from db
from flask_login import UserMixin
from sqlalchemy.sql import func
    
class Goals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    goaltype = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Times(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(10000))
    time = db.Column(db.String(10000))
    competition = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Questionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sleep = db.Column(db.Integer())
    stress = db.Column(db.Integer())
    fatigue = db.Column(db.Integer())
    color = db.Column(db.Integer())
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    reps = db.Column(db.Integer())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin): #Creating the user model
    id = db.Column(db.Integer, primary_key=True) #This userID is the primary key and unique to each user
    forename = db.Column(db.String(150))
    surname = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True) #unique=True ensures that no users have duplicate emails and usernames
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now()) #The date and time when this is stored is saved as a new column
    squads_id = db.Column(db.Integer, db.ForeignKey('squads.id'))
    squad = db.relationship('Squads', back_populates='user')
    role = db.Column(db.String(7))
    goals = db.relationship('Goals')
    journal = db.relationship('Journal')
    times = db.relationship('Times')
    attendance = db.relationship('Attendance')
    questionnaire = db.relationship('Questionnaire')
    exercise = db.relationship('Exercise')

class Squads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    squadName = db.Column(db.String(150), unique=True)
    squadCode = db.Column(db.String(4), unique=True)
    user = db.relationship('User', back_populates='squad')

