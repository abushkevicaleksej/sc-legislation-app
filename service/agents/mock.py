from .abstract.auth_agent import AuthAgent, AuthStatus
from .abstract.reg_agent import RegAgent, RegStatus
from .abstract.user_request_agent import RequestAgent, RequestStatus
from .abstract.directory_agent import DirectoryAgent, DirectoryStatus

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