import configparser


class Config:
    config = configparser.ConfigParser()
    config.read('config.ini')

    AGENTS_TO_LOAD = {
        "auth_agent": "service.agents.ostis.OstisAuthAgent",
        "reg_agent": "service.agents.ostis.OstisRegAgent",
        "user_request_agent": "service.agents.ostis.OstisUserRequestAgent",
    }
    OSTIS_URL = config['DEFAULT']['ostis_url']
    PROTOCOL = config['SERVER']['SC_SERVER_PROTOCOL']
    HOST = config['SERVER']['SC_SERVER_HOST']
    PORT = config['SERVER']['SC_SERVER_PORT']
    PROTOCOL_DEFAULT = config['SERVER']['SC_SERVER_PROTOCOL_DEFAULT']
    HOST_DEFAULT = config['SERVER']['SC_SERVER_HOST_DEFAULT']
    PORT_DEFAULT = config['SERVER']['SC_SERVER_PORT_DEFAULT']
