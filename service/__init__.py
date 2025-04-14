from flask import Flask
from flask_login import LoginManager

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    
    login_manager.init_app(app)
    
    from .views import main
    app.register_blueprint(main)

    from .agent_factory import load_agents
    app.config['agents'] = load_agents()
    
    app.secret_key = 'secret_key'
    
    from .handlers import register_error_handlers
    register_error_handlers(app)

    return app