from abc import ABC, abstractmethod
from enum import StrEnum

class RegStatus(StrEnum):
    CREATED = "created"
    EXISTS = "exists"

class Gender(StrEnum):
    MALE = "мужской"
    FEMALE = "женский"

class RegAgent(ABC):
    @abstractmethod
    def reg_agent(
        self,
        gender: str, 
        surname: str,
        name: str,
        fname: str,
        birthdate: str,
        reg_place: str,
        username: str,
        password: str
        ) -> dict:
        pass