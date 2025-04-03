from flask import Blueprint, request, jsonify
from flask import render_template

from .services import auth_agent, reg_agent

main = Blueprint("main", __name__)

@main.route("/index")
def index():
    return "Hello world!"

@main.route("/auth", methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username, password)
        auth_agent(username, password)
    return render_template('authorization.html')

@main.route("/reg", methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        gender = request.form.get("gender")
        surname = request.form.get("surname")
        name = request.form.get("name")
        fname = request.form.get("patronymic")
        reg_place = request.form.get("registration")
        birthdate = request.form.get("birthdate")
        username = request.form.get('login')
        password = request.form.get('password')
        reg_agent(gender=gender, surname=surname, name=name, fname=fname, reg_place=reg_place, birthdate=birthdate, username=username, password=password)
    return render_template('registration.html')

@main.route("/requests")
def requests():
    return '200 ok'

@main.route("/directory")
def directory():
    return 'directory route'

@main.route("/templates")
def templates():
    return 'templ route'

@main.route("/calendar")
def calendar():
    return 'calendar route'