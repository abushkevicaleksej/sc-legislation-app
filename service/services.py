from flask import current_app

from service.agents.abstract.auth_agent import AuthAgent
from service.agents.abstract.reg_agent import RegAgent
from service.agents.abstract.user_request_agent import RequestAgent
from service.agents.abstract.directory_agent import DirectoryAgent
from service.agents.abstract.event_agents import AddEventAgent, DeleteEventAgent, ShowEventAgent

def reg_agent(gender, surname: str, name: str, fname: str, birthdate, reg_place: str, username: str, password: str):
    agent: RegAgent = current_app.config['agents']['reg_agent']
    return agent.reg_agent(
        gender=gender, 
        surname=surname, 
        name=name, 
        fname=fname, 
        birthdate=birthdate, 
        reg_place=reg_place, 
        username=username, 
        password=password
        )

def auth_agent(username: str, password: str):
    agent: AuthAgent = current_app.config['agents']['auth_agent']
    return agent.auth_agent(
        username, 
        password
        )

def user_request_agent(content: str):
    agent: RequestAgent = current_app.config['agents']['user_request_agent']
    return agent.request_agent(content)

def directory_agent(content: str):
    agent: DirectoryAgent = current_app.config['agents']['directory_agent']
    return agent.directory_agent(
        content=content
        )

def add_event_agent(user_name: str, event_name: str, event_date: str, event_description: str):
    agent: AddEventAgent = current_app.config['agents']['add_event_agent']
    return agent.add_event_agent(
        user_name=user_name,
        event_name=event_name,
        event_date=event_date,
        event_description=event_description
    )

def delete_event_agent(event_name: str):
    agent: DeleteEventAgent = current_app.config['agents']['delete_event_agent']
    return agent.delete_event_agent(
        event_name=event_name
    )

def show_event_agent(user):
    agent: ShowEventAgent = current_app.config['agents']['show_event_agent']
    return agent.show_event_agent(
        user=user
    )