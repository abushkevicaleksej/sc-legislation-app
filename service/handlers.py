from flask import jsonify
from .exceptions import APIError, AgentError
from .schemas.base import SchemaValidationError


def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.code
        return response

    @app.errorhandler(404)
    def handle_not_found_error(error):
        return jsonify({
            "error": "not_found",
            "message": "The requested resource was not found."
        }), 404

    @app.errorhandler(SchemaValidationError)
    def handle_validation_error(error):
        return jsonify({
            "error": "validation_error",
            "message": "Invalid input.",
            "details": error.messages
        }), 400

    @app.errorhandler(AgentError)
    def handle_unexpected_error(error: AgentError):
        return jsonify({
            "error": "agent_error",
            "message": error.message
        }), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return jsonify({
            "error": "unexpected_error",
            "message": str(error)
        }), 500
