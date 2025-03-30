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

@main.route("/auth")
def auth():
    return render_template('authorization.html')


@main.route("/reg")
def reg():
    return render_template('registration.html')