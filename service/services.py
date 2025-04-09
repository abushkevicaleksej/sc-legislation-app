from flask import current_app

from service.agents.abstract.auth_agent import AuthAgent, AuthStatus
from service.agents.abstract.reg_agent import RegAgent, RegStatus


def reg_agent(gender, surname: str, name: str, fname: str, birthdate, reg_place: str, username: str, password: str):
    agent: RegAgent = current_app.config['agents']['reg_agent']
    return agent.reg_agent(gender=gender, 
                           surname=surname, 
                           name=name, 
                           fname=fname, 
                           birthdate=birthdate, 
                           reg_place=reg_place, 
                           username=username, 
                           password=password)


def auth_agent(username: str, password: str):
    agent: AuthAgent = current_app.config['agents']['auth_agent']
    return agent.auth_agent(username, password)