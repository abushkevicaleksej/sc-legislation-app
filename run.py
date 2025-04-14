from sc_kpm import ScServer
import config
from service import create_app

if __name__ == "__main__":
    app = create_app()
    
    try:
        server = ScServer(f"{config.Config.PROTOCOL_DEFAULT}://{config.Config.HOST_DEFAULT}:{config.Config.PORT_DEFAULT}")
        with server.connect():
            app.run()
    except:
        from service.exceptions import ScServerError
        raise ScServerError