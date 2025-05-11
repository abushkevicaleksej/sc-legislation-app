from .abstract.auth_agent import AuthAgent, AuthStatus
from .abstract.reg_agent import RegAgent, RegStatus
from .abstract.user_request_agent import RequestAgent, RequestStatus
from .abstract.directory_agent import DirectoryAgent, DirectoryStatus
from .abstract.event_agents import (
    AddEventStatus,
    AddEventAgent,
    DeleteEventStatus,
    DeleteEventAgent,
    ShowEventStatus,
    ShowEventAgent
)
from sc_client.models import ScAddr
class OstisAuthAgent(AuthAgent):
    def auth_agent(self, username: str, password: str):
        print(f"MockAgent: Pretend authenticating {username} - {password}")
        return {
            "status": AuthStatus.INVALID,
            "message": "Invalid credentials",
        }
    
class OstisRegAgent(RegAgent):
    def reg_agent(
        self,
        gender, 
        surname: str,
        name: str,
        fname: str,
        birthdate,
        reg_place: str,
        username: str,
        password: str
        ):
        print(f"MockAgent: Pretend registering {gender} - {surname} - {name} - {fname} - {birthdate} - {reg_place} - {username} - {password}")
        return {"status": RegStatus.CREATED}
    
class OstisUserRequestAgent(RequestAgent):
    def request_agent(
            self,
            content: str
            ):
        print(f"MockAgent: Pretend requesting {content}")
        return {"status": RequestStatus.VALID}
    
class OstisDirectoryAgent(DirectoryAgent):
    def directory_agent(
            self, 
            content, 
            ):
        print(f"MockAgent: Pretend requesting {content}")
        return {"status": DirectoryStatus.VALID}

class OstisAddEventAgent(AddEventAgent):
    def add_event_agent(self, 
                        user_name: str, 
                        event_name: str, 
                        event_date: str, 
                        event_description: str
                        ):
        print(f"MockAgent: Pretend requesting {event_name} {event_description}")
        return {"status": AddEventStatus.VALID}
    
class OstisDeleteEventAgent(DeleteEventAgent):
    def delete_event_agent(self, 
                        event_name: str, 
                        ):
        print(f"MockAgent: Pretend requesting {event_name}")
        return {"status": DeleteEventStatus.VALID}

class OstisShowEventAgent(ShowEventAgent):
    def show_event_agent(self, 
                        user: ScAddr, 
                        ):
        print(f"MockAgent: Pretend requesting {user}")
        return {"status": ShowEventStatus.VALID}