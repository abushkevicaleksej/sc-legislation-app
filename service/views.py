from flask import Blueprint, request, jsonify

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
    return "200"


@main.route("/reg")
def reg():
    return "200"