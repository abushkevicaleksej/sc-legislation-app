from .abstract.auth_agent import AuthAgent, AuthStatus
from .abstract.reg_agent import RegAgent, RegStatus, Gender

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
        gender: str, 
        surname: str,
        name: str,
        fname: str,
        birthdate: str,
        reg_place: str,
        username: str,
        password: str
        ):
        print(f"MockAgent: Pretend registering {gender} - {surname} - {name} - {fname} - {birthdate} - {reg_place} {username} - {password}")
        return {"status": RegStatus.CREATED}