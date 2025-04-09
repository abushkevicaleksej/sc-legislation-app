from service import create_app
from sc_client.client import connect, is_connected
from sc_kpm import ScServer
import config
from service.exceptions import ScServerError

app = create_app()

if __name__ == "__main__":
    try:
        server = ScServer(f"{config.Config.PROTOCOL_DEFAULT}://{config.Config.HOST_DEFAULT}:{config.Config.PORT_DEFAULT}")
        with server.connect():
            app.run()
    except:
        raise ScServerError