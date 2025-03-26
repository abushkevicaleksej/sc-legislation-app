from .abstract.auth_agent import AuthAgent, RegStatus, AuthStatus


class OstisAuthAgent(AuthAgent):
    def reg_agent(self, username: str, password: str):
        print(f"MockAgent: Pretend registering {username} - {password}")
        return {"status": RegStatus.CREATED}

    def auth_agent(self, username: str, password: str):
        print(f"MockAgent: Pretend authenticating {username} - {password}")
        return {
            "status": AuthStatus.INVALID,
            "message": "Invalid credentials",
        }
    
#TODO add more agents like dat ^_^