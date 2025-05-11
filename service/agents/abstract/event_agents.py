from abc import ABC, abstractmethod
from enum import StrEnum
from sc_client.models import ScAddr

class AddEventStatus(StrEnum):
    VALID = "Valid"
    INVALID = "Invalid"

class AddEventAgent(ABC):
    @abstractmethod
    def add_event_agent(self, user_name: str, event_name: str, event_date: str, event_description: str):
        pass

class DeleteEventStatus(StrEnum):
    VALID = "Valid"
    INVALID = "Invalid"

class DeleteEventAgent(ABC):
    @abstractmethod
    def delete_event_agent(self, username: str, event_name: str):
        pass

class ShowEventStatus(StrEnum):
    VALID = "Valid"
    INVALID = "Invalid"

class ShowEventAgent(ABC):
    @abstractmethod
    def show_event_agent(self, username: str):
        pass