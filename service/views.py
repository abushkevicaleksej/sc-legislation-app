from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from sc_client.client import get_link_content, search_by_template

from .models import (
    find_user_by_username, 
    collect_user_info
    )

from .utils.string_processing import string_processing
from .utils.ostis_utils import get_term_titles
from .services import (
    auth_agent, 
    reg_agent, 
    user_request_agent, 
    directory_agent, 
    add_event_agent, 
    delete_event_agent, 
    show_event_agent
)

from .forms import LoginForm, RegistrationForm, AddEventForm

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
    users = get_term_titles() 
    print(users)
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

@main.route("/show_calendar")
@login_required
def show_calendar():
    return render_template("calendar.html")

@main.route("/add_event")
@login_required
def add_event():
    user = find_user_by_username(get_link_content(current_user.username)[0].data)
    response = add_event_agent(user, "event1", "12.04.2025", "hahaha")
    return redirect(url_for('main.show_calendar'))

@main.route("/requests", methods=['GET', 'POST'])
@login_required
def requests():
    if request.method == 'POST':
        content = request.form.get("request_entry")
    else:
        content = request.args.get('q')

    if content:
        processed_terms = string_processing(content)
        
        all_results = []
        all_queries = []
        
        for term in processed_terms:
            response = user_request_agent(content=term)
            if response["message"] is not None:
                try:
                    results = [{
                        'term': item.term,
                        'content': item.content,
                        'related_concepts': item.related_concepts,
                        'related_articles': item.related_articles
                    } for item in response["message"]]
                except AttributeError as e:
                    print(f"Ошибка формата данных: {e}")
                    results = []

                all_results.extend(results)
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

    return render_template("requests-results.html", 
                         query=query, 
                         results=results)

@main.route("/directory", methods=['GET', 'POST'])
@login_required
def directory():
    term_titles = get_term_titles()
    if request.method == 'POST':
        content = request.form.get("directory_entry")
        asked = directory_agent(content=content)
        
        if asked["message"] is not None:
            session['search_query'] = content
            session['search_results'] = asked["message"]
            return redirect(url_for('main.directory_results'))
        else:
            flash('Ничего не найдено', 'warning')
            return render_template("directory.html", term_titles=term_titles)
    
    return render_template("directory.html", term_titles=term_titles)

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
