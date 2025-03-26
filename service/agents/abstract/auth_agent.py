from abc import ABC, abstractmethod
from enum import StrEnum


class RegStatus(StrEnum):
    CREATED = "created"
    EXISTS = "exists"


class AuthStatus(StrEnum):
    VALID = "valid"
    INVALID = "invalid"


class AuthAgent(ABC):
    @abstractmethod
    def reg_agent(self, username: str, password: str) -> dict:
        pass

    @abstractmethod
    def auth_agent(self, username: str, password: str) -> dict:
        pass