from flask import Blueprint, request, jsonify
from flask import render_template
from .schemas.input import AuthSchema as AuthInputSchema
from .schemas.output import AuthSchema as AuthOutputSchema
from .schemas.output import RegSchema as RegOutputSchema
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

@main.route("/reg")
def reg():
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