class ScServerError(Exception):
    message = "Failed to connect to SC-server! Goodbye."

class APIError(Exception):
    code = 400
    message = "A client error occurred."
    description = None

    def __init__(self, code=None, message=None, description=None):
        if code is not None:
            self.code = code
        if message is not None:
            self.message = message
        if description is not None:
            self.description = description

    def to_dict(self):
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "description": self.description,
        }


class FieldRequiredError(APIError):
    message = "A required field is missing."
    description = {"field": "Specify the field name causing the error."}


class AgentError(APIError):
    code = 500
    message = "An unexpected agent error"

class ParseDataError(APIError):
    code = 666
    message = "An unexpected iput data"    