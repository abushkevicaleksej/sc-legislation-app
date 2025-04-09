from abc import ABC, abstractmethod
from enum import StrEnum


class RequestStatus(StrEnum):
    VALID = "valid"
    INVALID = "invalid"


class RequestAgent(ABC):
    @abstractmethod
    def request_agent(self, content: str) -> dict:
        pass