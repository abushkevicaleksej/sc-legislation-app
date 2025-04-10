from abc import ABC, abstractmethod
from enum import StrEnum


class AuthStatus(StrEnum):
    VALID = "Valid"
    INVALID = "Invalid"


class AuthAgent(ABC):
    @abstractmethod
    def auth_agent(self, username: str, password: str) -> dict:
        pass