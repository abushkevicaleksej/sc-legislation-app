from flask import current_app

from service.agents.abstract.auth_agent import AuthAgent
from service.agents.abstract.reg_agent import RegAgent


def reg_agent(gender: str, surname: str, name: str, fname: str, birthdate: str, reg_place: str, username: str, password: str):
    agent: RegAgent = current_app.config['agents']['reg_agent']
    return agent.reg_agent(gender, surname, name, fname, birthdate, reg_place, username, password)


def auth_agent(username: str, password: str):
    agent: AuthAgent = current_app.config['agents']['auth_agent']
    return agent.auth_agent(username, password)