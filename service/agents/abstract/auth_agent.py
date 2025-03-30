from abc import ABC, abstractmethod
from enum import StrEnum


class AuthStatus(StrEnum):
    VALID = "valid"
    INVALID = "invalid"


class AuthAgent(ABC):
    @abstractmethod
    def auth_agent(self, username: str, password: str) -> dict:
        pass