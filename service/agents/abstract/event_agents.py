from abc import ABC, abstractmethod
from enum import StrEnum
from sc_client.models import ScAddr

class AddEventStatus(StrEnum):
    """
    Перечисление для представления статусов результата выполнения агента добавления события
    """
    VALID = "Valid"
    INVALID = "Invalid"

class AddEventAgent(ABC):
    """
    Абстрактный класс для реализации агента добавления события
    """
    @abstractmethod
    def add_event_agent(self, user: ScAddr, event_name: str, event_date, event_description: str):
        """
        Абстрактный метод для запуска агента добавления события
        :param user: Адрес ноды пользователя
        :param event_name: Название события
        :param event_date: Дата события
        :param event_description: Описание события
        :return:
        """
        pass

class DeleteEventStatus(StrEnum):
    """
    Перечисление для представления статусов результата выполнения агента удаления события
    """
    VALID = "Valid"
    INVALID = "Invalid"

class DeleteEventAgent(ABC):
    """
    Абстрактный класс для реализации агента удаления события
    """
    @abstractmethod
    def delete_event_agent(self, event_name: str):
        """
        Абстрактный метод для запуска агента удаления события
        :param event_name: Название события
        :return:
        """
        pass

class ShowEventStatus(StrEnum):
    """
    Перечисление для представления статусов результата выполнения агента просмотра события
    """
    VALID = "Valid"
    INVALID = "Invalid"

class ShowEventAgent(ABC):
    """
    Абстрактный класс для реализации агента просмотра события
    """
    @abstractmethod
    def show_event_agent(self, user: ScAddr):
        """
        Абстрактный метод для запуска агента просмотра события
        :param user: Адрес ноды пользователя
        :return:
        """
        pass