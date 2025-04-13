from abc import ABC, abstractmethod
from enum import StrEnum


class DirectoryStatus(StrEnum):
    VALID = "Valid"
    INVALID = "Invalid"


class DirectoryAgent(ABC):
    @abstractmethod
    def directory_agent(self, content: str) -> dict:
        pass