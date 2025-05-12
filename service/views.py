from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from sc_client.client import get_link_content, search_by_template

from .models import (
<<<<<<< HEAD
    find_user_by_username, 
    collect_user_info,
=======
    find_user_by_username,
    collect_user_info
>>>>>>> 645679bcbec963fd69f93b7fb5dfeb446ed5047d
    )

from .utils.string_processing import string_processing
from .utils.ostis_utils import get_term_titles, get_event_by_date
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
    """
    Метод для реализации ендпоинта, который выводит текущего пользователя
    :return: Разметка страницы
    """
    users = get_term_titles()
    print(users)
    return f"<pre>{str(current_user)}</pre>"

@main.route("/auth", methods=['GET','POST'])
def auth():
    """
    Метод для реализации эндпоинта аутентификации
    :return: Разметка страницы
    """
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
    """
    Метод для реализации эндпоинта регистрации
    :return: Разметка страницы
    """
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
    """
    Метод для реализации эндпоинта выхода с профиля
    :return: Разметка страницы
    """
    logout_user()
    return redirect(url_for('main.auth'))

@main.route("/show_calendar")
@login_required
def show_calendar():
    """
    Метод для реализации эндпоинта календаря
    :return: Разметка страницы
    """
    user = get_link_content(current_user.username)[0].data
    selected_date = request.args.get("selected_date")
    
    events = get_event_by_date(selected_date, user) if selected_date else []
    
    return render_template("calendar.html", 
                         events=events.events if events else [],
                         form=AddEventForm(),
                         selected_date=selected_date)

@main.route("/add_event", methods=["POST"])
@login_required
def add_event():
<<<<<<< HEAD
    form = AddEventForm()
    if form.validate_on_submit():
        user = get_link_content(current_user.username)[0].data
        add_event_agent(
            user_name=user,
            event_name=form.title.data,
            event_date=form.date.data,
            event_description=form.description.data
        )
    return redirect(url_for('main.show_calendar', selected_date=form.date.data))
=======
    """
    Метод для реализации эндпоинта добавления события
    :return: Разметка страницы
    """
    user = get_link_content(current_user.username)[0].data
    print(user)
    response = add_event_agent(user_name=user,
                               event_name="event1",
                               event_date="12.04.2025",
                               event_description="hahaha"
                               )
    return redirect(url_for('main.show_calendar'))
>>>>>>> 645679bcbec963fd69f93b7fb5dfeb446ed5047d

@main.route("/delete_event")
@login_required
def delete_event():
    user = get_link_content(current_user.username)[0].data
    print(user)
    response = delete_event_agent(username=user,
                               event_name="event1",
                               )
    return redirect(url_for('main.show_calendar'))

@main.route("/requests", methods=['GET', 'POST'])
@login_required
def requests():
    """
    Метод для реализации эндпоинта юридических запросов
    :return: Разметка страницы
    """
    if request.method == 'POST':
        content = request.form.get("request_entry")
        if content == '':
            flash(f"Для поиска по справочнику требуется ввести текст", category="empty-text-error")
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
                    if len(response["message"]) == 0:
                        flash(f"По вашему запросу ничего не найдено", category="empty-result-error")
                        return render_template("requests.html")
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
    """
    Метод для реализации эндпоинта просмотра результатов юридических запросов
    :return: Разметка страницы
    """
    query = session.get('search_query', '')
    results = session.get('search_results', [])

    return render_template("requests-results.html", 
                         query=query, 
                         results=results)

@main.route("/directory", methods=['GET', 'POST'])
@login_required
def directory():
    """
    Метод для реализации эндпоинта поиска
    :return: Разметка страницы
    """
    term_titles = get_term_titles()
    if request.method == 'POST':
        content = request.form.get("directory_entry")
        if content == '':
            flash(f"Для поиска по справочнику требуется ввести текст", category="empty-text-error")
            return render_template("directory.html", term_titles=term_titles)
        print(content)
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
    """
    Метод для реализации эндпоинта просмотра результатов поиска
    :return: Разметка страницы
    """
    query = session.get('search_query', '')
    results = session.get('search_results', [])
    return render_template("directory-results.html", query=query, results=results)

@main.route("/templates")
@login_required
def templates():
    """
    Метод для реализации эндпоинта шаблонов
    :return: Разметка страницы
    """
    return render_template("templates.html")
