from flask import current_app

<<<<<<< HEAD
from service.agents.abstract.auth_agent import AuthAgent
from service.agents.abstract.reg_agent import RegAgent
from service.agents.abstract.user_request_agent import RequestAgent
=======
from service.agents.abstract.auth_agent import AuthAgent, AuthStatus
from service.agents.abstract.reg_agent import RegAgent, RegStatus
>>>>>>> 48097e9 (auth and reg works correctly. needs to reprint html)


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

def user_request_agent(content: str):
    agent: RequestAgent = current_app.config['agents']['user_request_agent']
    return agent.request_agent(content)