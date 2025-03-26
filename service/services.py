from flask import current_app

from service.agents.abstract.auth_agent import AuthAgent


def reg_agent(username: str, password: str):
    agent: AuthAgent = current_app.config['agents']['auth_agent']
    return agent.reg_agent(username, password)


def auth_agent(username: str, password: str):
    agent: AuthAgent = current_app.config['agents']['auth_agent']
    return agent.auth_agent(username, password)