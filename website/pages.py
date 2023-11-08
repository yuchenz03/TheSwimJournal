from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify #From the flask application, import Blueprint
from . import db
from .models import User
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required
import sqlite3
from random import randint
import json



pages = Blueprint("pages", __name__) #The blueprint name is now pages

@pages.route("/conversionTool") 
def conversionTool():
    return render_template("conversionTool.html") #renders conversion tool template

@pages.route("/home")
def homepage():
    return render_template("homepage.html")   