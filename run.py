from sc_kpm import ScServer
from config import Config
from service import create_app

if __name__ == "__main__":
    app = create_app()
    
    try:
        server = ScServer(f"{Config.PROTOCOL_DEFAULT}://{Config.HOST_DEFAULT}:{Config.PORT_DEFAULT}")
        with server.connect():
            app.run()
    except:
        from service.exceptions import ScServerError
        raise ScServerError