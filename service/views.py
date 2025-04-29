from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from .models import User, load_user, find_user_by_username

from .services import auth_agent, reg_agent, user_request_agent, directory_agent

from .forms import LoginForm, RegistrationForm

main = Blueprint("main", __name__)

@main.route("/index")
@login_required
def index():
    return "Hello world!"

@main.route("/auth", methods=['POST'])
def auth():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.directory'))
    if form.validate_on_submit():
        user = find_user_by_username(form.username.data)
        auth_response = auth_agent(form.username.data, form.password.data)
        if auth_response["status"] == "Valid":
            login_user(user)
            return redirect(url_for('main.directory'))
    return render_template('authorization.html', form=form)

@main.route("/reg", methods=['POST'])
def reg():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.directory'))
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

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.auth'))

@main.route("/protected")
@login_required
def protected():
    return "Только для авторизованных"

@main.route("/reg", methods=['GET', 'POST'])
def reg():
    if current_user.is_authenticated:
        return redirect(url_for('main.directory'))
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
@login_required
def add_event():
    return render_template("add-event.html")

@main.route("/show_calendar")
@login_required
def show_calendar():
    return render_template("calendar.html")

@main.route("/doc")
@login_required
def doc():
    return render_template("document.html")

@main.route("/templates")
@login_required
def templs():
    return render_template("templates.html")

@main.route("/requests", methods=['GET', 'POST'])
@login_required
def requests():
    if request.method == 'POST':
        content = request.form.get("request_entry")
        asked = user_request_agent(content=content)
        if asked["message"] is not None:
            session['search_query'] = content
            session['search_results'] = asked["message"]
            return redirect(url_for('main.requests_results'))
        else:
            flash('Ничего не найдено', 'warning')
            return render_template("requests.html")
    return render_template("requests.html")

@main.route("/requests_results")
@login_required
def requests_results():
    query = session.get('search_query', '')
    results = session.get('search_results', [])
    return render_template("requests-results.html", query=query, results=results)

@main.route("/directory", methods=['GET', 'POST'])
@login_required
def directory():
    if request.method == 'POST':
        content = request.form.get("directory_entry")
        asked = directory_agent(content=content)
        if asked["message"] is not None:
            session['search_query'] = content
            session['search_results'] = asked["message"]
            return redirect(url_for('main.directory_results'))
        else:
            flash('Ничего не найдено', 'warning')
            return render_template("directory.html")
    return render_template("directory.html")

@main.route("/directory_results")
@login_required
def directory_results():
    query = session.get('search_query', '')
    results = session.get('search_results', [])
    return render_template("directory-results.html", query=query, results=results)

@main.route("/templates")
@login_required
def templates():
    return render_template("templates.html")

@main.route("/show_calendar")
@login_required
def calendar():
    return render_template("calendar.html")