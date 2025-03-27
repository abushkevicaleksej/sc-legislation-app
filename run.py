from service import create_app
from sc_client.client import connect, is_connected
import config
from service.exceptions import ScServerError

app = create_app()

if __name__ == "__main__":
    try:
        connect(config.Config.OSTIS_URL)
    except:
        raise ScServerError
    if is_connected():
        app.run()