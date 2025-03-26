import configparser


class Config:
    config = configparser.ConfigParser()
    config.read('config.ini')

    AGENTS_TO_LOAD = {
        "auth_agent": "service.agents.mock.OstisAuthAgent",
    }
    OSTIS_URL = config['DEFAULT']['ostis_url']
