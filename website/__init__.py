#Importing all the dependencies
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


#Creating the swimJournal.db database
db = SQLAlchemy()
DB_NAME = "swimJournal.db"

#This step is required to create a flask application - any website using flask requires this step.
def create_app():
    app = Flask(__name__) #variable name is name of the Flask app. __name__ is the name of the module used to run this app.
    app.config['SECRET_KEY'] = 'taylorswiftisthegoat'  #secret key
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app) 

    from .auth import auth #there is a dot before pages after from because the function is within a python package. If it wasn't, you wouldn't need the dot
    from .swimmerPages import swimmerPages
    from .coachPages import coachPages
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(swimmerPages, url_prefix='/swimmer')
    app.register_blueprint(coachPages, url_prefix='/coach')

    from .models import User #This must be done to create the user table when we open the database
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager() #This is a login manager - allows logins to happen
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id): #This function allows us to access a particular user given their id
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')