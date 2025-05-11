from flask import Flask
from flask_login import LoginManager
from flask_caching import Cache
from .encoder import SCJSONEncoder

login_manager = LoginManager()

login_manager.login_view = 'main.auth'
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

MAX_SESSION_SIZE = 4096

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    cache.init_app(app)
    login_manager.init_app(app)
    from .views import main
    app.register_blueprint(main)

    from .agent_factory import load_agents
    app.config['agents'] = load_agents()
    app.json_encoder = SCJSONEncoder
    app.secret_key = 'secret_key'
    
    from .handlers import register_error_handlers
    register_error_handlers(app)

    return app