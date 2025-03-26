from flask import Blueprint, request, jsonify

from .schemas.input import AuthSchema as AuthInputSchema
from .schemas.output import AuthSchema as AuthOutputSchema
from .schemas.output import RegSchema as RegOutputSchema
from .services import auth_agent, reg_agent

main = Blueprint("main", __name__)


@main.route("/auth", methods=["POST"])
def auth():
    data = AuthInputSchema().load(request.get_json())

    username = data["username"]
    password = data["password"]

    output = auth_agent(username, password)
    return jsonify(AuthOutputSchema().dump(output)), 200


@main.route("/reg", methods=["POST"])
def reg():
    data = AuthInputSchema().load(request.get_json())

    username = data["username"]
    password = data["password"]

    output = reg_agent(username, password)

    return jsonify(RegOutputSchema().dump(output)), 200