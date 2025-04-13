from flask import Blueprint, request, jsonify
from flask import render_template, redirect, url_for, session, flash
from flask_login import current_user, login_user


from .services import auth_agent, reg_agent, user_request_agent, directory_agent
from .errors import ErrorMessages

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
            #TODO обернуть абстракцию вокруг юзера
            #TODO нужен манагер всех юзеров
            #TODO login_user(user)
            return redirect(url_for('main.directory'))
        else:
            flash(ErrorMessages.error_auth(ErrorMessages))
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
    if request.method == 'POST':
        content = request.form.get("request_entry")
        asked = user_request_agent(content)
        print(asked["message"])
        if asked["message"] is not None:
            return redirect(url_for('main.requests_results'))
        else:
            return render_template("requests.html")
    return render_template("requests.html")

@main.route("/requests_results")
def requests_results():
    return render_template("requests-results.html")

@main.route("/directory", methods=['GET', 'POST'])
def directory():
    if request.method == 'POST':
        content = request.form.get("directory_entry")
        print(content)
        asked = directory_agent(content=content)
        print(asked["message"])
        if asked["message"] is not None:
            return redirect(url_for('main.directory_results'))
        else:
            return render_template("directory.html")
    return render_template("directory.html")

@main.route("/directory_results")
def directory_results():
    return render_template("directory-results.html")

@main.route("/templates")
def templates():
    return render_template("templates.html")

@main.route("/show_calendar")
def calendar():
    return render_template("calendar.html")