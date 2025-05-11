from abc import ABC, abstractmethod
from enum import StrEnum

class RegStatus(StrEnum):
    """
    Перечисление для представления статусов результата выполнения агента регистрации
    """
    CREATED = "Valid"
    EXISTS = "Invalid"

class Gender(StrEnum):
    """
    Перечисление для представления полов пользователя
    """
    MALE = "мужской"
    FEMALE = "женский"

class RegAgent(ABC):
    """
    Абстрактный класс для реализации агента регистрации
    """
    @abstractmethod
    def reg_agent(
        self,
        gender: str, 
        surname: str,
        name: str,
        fname: str,
        birthdate,
        reg_place: str,
        username: str,
        password: str
        ) -> dict:
        """
        Абстрактный метод для запуска агента регистрации
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
        pass