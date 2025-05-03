from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from .models import find_user_by_username

from .utils.string_processing import string_processing

from .services import auth_agent, reg_agent, user_request_agent, directory_agent

from .forms import LoginForm, RegistrationForm

main = Blueprint("main", __name__)

@main.route("/index")
@login_required
def index():
    return "Hello world!"

@main.route("/protected")
@login_required
def protected():
    return "Только для авторизованных"

@main.route("/about")
def about():
    return f"<pre>{str(current_user)}</pre>"

@main.route("/auth", methods=['GET','POST'])
def auth():
    if current_user.is_authenticated:
        return redirect(url_for('main.directory'))
    form = LoginForm()
    if form.validate_on_submit():
        user = find_user_by_username(form.username.data)
        auth_response = auth_agent(form.username.data, form.password.data)
        if auth_response["status"] == "Valid":
            login_user(user)
            return redirect(url_for('main.directory'))
    return render_template('authorization.html', form=form)

@main.route("/reg", methods=['GET', 'POST'])
def reg():
    if current_user.is_authenticated:
        return redirect(url_for('main.directory'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        reg_response = reg_agent(
            gender=form.gender.data,
            surname=form.surname.data,
            name=form.name.data,
            fname=form.patronymic.data,
            reg_place=form.reg_place.data,
            birthdate=form.birthdate.data,
            username=form.username.data,
            password=form.password.data
        )
        if reg_response["status"] == "Valid":
            user = find_user_by_username(form.username.data)
            login_user(user)
            return redirect(url_for('main.directory'))
    return render_template('registration.html', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.auth'))

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

#todo RAG
@main.route("/requests", methods=['GET', 'POST'])
@login_required
def requests():
    if request.method == 'POST':
        content = request.form.get("request_entry")
        processed_terms = string_processing(content)
        
        all_results = []
        all_queries = []
        
        for term in processed_terms:
            response = user_request_agent(content=term)
            if response["message"] is not None:
                all_results.extend(response["message"])
                all_queries.append(term)
        
        if all_results:
            session['search_query'] = ", ".join(all_queries)
            session['search_results'] = all_results
            return redirect(url_for('main.requests_results'))
        
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