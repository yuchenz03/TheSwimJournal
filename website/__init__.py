#Importing all the dependencies
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

#Creating the swimJournal.db database
db = SQLAlchemy()
DB_NAME = "swimJournal.db"

#This step is required to create a flask application - any website using flask requires this step.
def create_app():
    app = Flask(__name__) #variable name is name of the Flask app. __name__ is the name of the module used to run this app.
    app.config['SECRET_KEY'] = 'taylorswiftisthegoat'  #creating a secret key
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' #Configure SQLAlchemy to use a SQLite database with the name swimJournal.db
    db.init_app(app) #Initialize the SQLAlchemy extension

    from .auth import auth #import the function auth from the python package auth 
    from .swimmerPages import swimmerpages #import the blueprint swimmerpages from swimmerPages.py
    from .coachPages import coachpages #import the blueprint coachpages from coachPages.py
    app.register_blueprint(auth, url_prefix='/') #set the url prefix for pages from the auth pages to be '/'
    app.register_blueprint(swimmerpages, url_prefix='/swimmer') #set the url prefix for pages from swimmerpages to be /swimmer
    app.register_blueprint(coachpages, url_prefix='/coach') #set the url prefix for pages from coachpages to be /coach

    from .models import User, Exercise, Event #import all tables from the models page
    #Create database tables using the models page
    with app.app_context():
        db.create_all()
    
        first_record = Event.query.first()
        if first_record == None:
            #Initializing values in my database  
            #initializing values in the exercise table
            newExercise = Exercise(name="Bench Press") #Add bench press exercise
            db.session.add(newExercise) #add this exercise to the database
            newExercise = Exercise(name="Squat Pause") #Add squat pause exercise
            db.session.add(newExercise) #add this exercise to the database
            newExercise = Exercise(name="Hollow Hold") #Add hollow hold exercise
            db.session.add(newExercise) #add this exercise to the database
            db.session.commit() #save the database
            
            #initializing values in the event table
            meterdistances = [25, 50, 100, 200, 400, 800, 1500] #types of distances available in meter pools
            yarddistances = [25, 50, 100, 200, 500, 1000, 1600] #types of distances available in yard pools
            strokes = ['Free', 'Back', 'Breast', 'Fly'] #the four strokes in swimming
            genders = ['M', 'F'] #two different genders
            events = [] #initializing events list
            
            #initializing the event swam in meter pools
            for stroke in strokes: #for each stroke
                for distance in meterdistances: #for each distance in a meter pool
                    if distance == 25 or distance == 50:
                        numOfSplits = 0
                    elif distance == 100:
                        numOfSplits = 2
                    elif distance == 200:
                        numOfSplits = 4
                    elif distance == 400:
                        numOfSplits = 4
                    elif distance == 800:
                        numOfSplits = 8
                    elif distance == 1500:
                        numOfSplits = 15
                    for gender in genders: #for each gender
                        events.append(Event(gender=gender, stroke=stroke, poolDistance="SCM", #add an event for SCM
                                            distance=str(distance)+"m", numOfSplits=numOfSplits, baseTime=None))
                        events.append(Event(gender=gender, stroke=stroke, poolDistance="LCM", #add an event for LCM
                                            distance=str(distance)+"m", baseTime=None))
                if stroke == "Free": #After free events have been appended
                    meterdistances = meterdistances[:4] #remove last four distances from list
            
            #initializing the events swam in yard pools
            for stroke in strokes:
                for distance in yarddistances:
                    if distance == 25 or distance == 50:
                        numOfSplits = 0
                    elif distance == 100:
                        numOfSplits = 2
                    elif distance == 200:
                        numOfSplits = 4
                    elif distance == 500:
                        numOfSplits = 5
                    elif distance == 1000:
                        numOfSplits = 10
                    elif distance == 1600:
                        numOfSplits = 16
                    for gender in genders:
                        events.append(Event(gender=gender, stroke=stroke, poolDistance="SCY", 
                                            distance=str(distance)+"y", numOfSplits=numOfSplits, baseTime=None))
                if stroke == "Free":
                    yarddistances = yarddistances[:4]
            
            #separately initializing the IM events in both meters and yards
            for gender in genders: 
                events.append(Event(gender=gender, stroke="IM", poolDistance="SCM", 
                            distance="100m", numOfSplits=4, baseTime=None))
                events.append(Event(gender=gender, stroke="IM", poolDistance="SCM", 
                            distance="200m", numOfSplits=4, baseTime=None))
                events.append(Event(gender=gender, stroke="IM", poolDistance="SCM", 
                            distance="400m", numOfSplits=8, baseTime=None))
                events.append(Event(gender=gender, stroke="IM", poolDistance="LCM", 
                            distance="200m", numOfSplits=4, baseTime=None))
                events.append(Event(gender=gender, stroke="IM", poolDistance="LCM", 
                            distance="400m", numOfSplits=8, baseTime=None))
                events.append(Event(gender=gender, stroke="IM", poolDistance="SCY", 
                            distance="100m", numOfSplits=4, baseTime=None))
                events.append(Event(gender=gender, stroke="IM", poolDistance="SCY", 
                            distance="200m", numOfSplits=4, baseTime=None))
                events.append(Event(gender=gender, stroke="IM", poolDistance="SCY", 
                            distance="400m", numOfSplits=8, baseTime=None))
            for event in events:
                db.session.add(event)
                db.session.commit()

    login_manager = LoginManager() #Initializes a login manager - allows logins to happen
    login_manager.login_view = 'auth.login' #Set the default login to the login endpoint in auth blueprint
    login_manager.init_app(app) #Initialize flask login extension to allow logins

    #This function allows us to access a particular user given their id
    @login_manager.user_loader #Decorator to define the user loader callback for Flask-Login
    def load_user(id): #Function with the userID parameter that retrieves any user.
        return User.query.get(int(id)) #returning the user that has the specified ID

    return app #return the flask app instance


def create_database(app): #A function that creates the database designed in the flask app
    if not path.exists('website/' + DB_NAME): #if there isn't already a database with the same name created
        db.create_all() #then create the database
        print('Created Database!')  #print "Created database" in the terminal as a confirmation message
        

