from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify #From the flask application, import Blueprint
from . import db
from .models import User
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required
import sqlite3
from random import randint
import json
