from flask import Blueprint, request, jsonify
from flask import render_template, redirect, url_for, session

from .services import auth_agent, reg_agent, user_request_agent

main = Blueprint("main", __name__)

@main.route("/index")
def index():
    return "Hello world!"

@main.route("/auth", methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        response = auth_agent(username, password)
        print(f"response {response["status"]}")
        if response["status"] == "Valid":
            return redirect(url_for('main.directory'))
        else:
            return render_template("authorization.html")
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
        response = reg_agent(
            gender=gender, 
            surname=surname, 
            name=name, 
            fname=fname, 
            reg_place=reg_place, 
            birthdate=birthdate, 
            username=username, 
            password=password
            )
        if response["status"] == "Valid":
            return redirect(url_for('main.directory'))
        else:
            return render_template('registration.html') 
    return render_template('registration.html')

@main.route("/add-event")
def add_event():
    return render_template("add-event.html")

@main.route("/show_calendar")
def show_calendar():
    return render_template("calendar.html")

@main.route("/doc")
def doc():
    return render_template("document.html")

@main.route("/templates")
def templs():
    return render_template("templates.html")

@main.route("/requests", methods=['GET', 'POST'])
def requests():
    print("GO")
    if request.method == 'POST':
        print("GO")
        content = request.form.get("request_entry")
        print(content)
        user_request_agent(content)
        return render_template("requests.html")
    return render_template("requests.html")

@main.route("/requests_results")
def requests_results():
    return render_template("requests-results.html")

@main.route("/directory")
def directory():
    return render_template("directory.html")

@main.route("/templates")
def templates():
    return render_template("templates.html")

@main.route("/show_calendar")
def calendar():
    return render_template("calendar.html")