from flask import current_app

from service.agents.abstract.auth_agent import AuthAgent
from service.agents.abstract.reg_agent import RegAgent
from service.agents.abstract.user_request_agent import RequestAgent
from service.agents.abstract.directory_agent import DirectoryAgent
from service.agents.abstract.event_agents import AddEventAgent, DeleteEventAgent, ShowEventAgent

def reg_agent(gender, surname: str, name: str, fname: str, birthdate, reg_place: str, username: str, password: str):
    """
    Метод для запуска агента регистрации
    :param gender: Пол пользователя для регистрации
    :param surname: Фамилия пользователя для регистрации
    :param name: Имя пользователя для регистрации
    :param fname: Отчество пользователя для регистрации
    :param birthdate: Дата рождения пользователя для регистрации
    :param reg_place: Место регистрации пользователя для регистрации
    :param username: Логин пользователя для регистрации
    :param password: Пароль пользователя для регистрации
    :return: Словарь со статусом результата выполнения агента регистрации
    """
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
    """
    Метод для запуска агента аутентификации
    :param username: Логин пользователя для аутентификации
    :param password: Пароль пользователя для аутентификации
    :return: Словарь со статусом результата выполнения агента аутентификации
    """
    agent: AuthAgent = current_app.config['agents']['auth_agent']
    return agent.auth_agent(
        username, 
        password
        )

def user_request_agent(content: str):
    """
    Метод для запуска агента юридических запросов
    :param content: Контент, по которому происходит поиск в БЗ
    :return: Словарь со статусом результата выполнения агента аутентификации
    """
    agent: RequestAgent = current_app.config['agents']['user_request_agent']
    return agent.request_agent(content)

def directory_agent(content: str):
    """
    Метод для запуска агента поиска
    :param content: Контент, по которому происходит поиск в БЗ
    :return: Словарь со статусом результата выполнения агента аутентификации
    """
    agent: DirectoryAgent = current_app.config['agents']['directory_agent']
    return agent.directory_agent(
        content=content
        )

def add_event_agent(user, event_name: str, event_date, event_description: str):
    """
    Метод для запуска агента добавления события
    :param user: Адрес ноды пользователя
    :param event_name: Название события
    :param event_date: Дата события
    :param event_description: Описание события
    :return: Словарь со статусом результата выполнения агента добавления события
    """
    agent: AddEventAgent = current_app.config['agents']['add_event_agent']
    return agent.add_event_agent(
        user=user,
        event_name=event_name,
        event_date=event_date,
        event_description=event_description
    )

def delete_event_agent(event_name: str):
    """
    Метод для запуска агента удаления события
    :param event_name: Название события
    :return: Словарь со статусом результата выполнения агента удаления события
    """
    agent: DeleteEventAgent = current_app.config['agents']['delete_event_agent']
    return agent.delete_event_agent(
        event_name=event_name
    )

def show_event_agent(user):
    """
    Метод для запуска агента просмотра события
    :param user: Адрес ноды пользователя
    :return: Словарь со статусом результата выполнения агента просмотра события
    """
    agent: ShowEventAgent = current_app.config['agents']['show_event_agent']
    return agent.show_event_agent(
        user=user
    )