import importlib
from config import Config


def load_agents():
    """
    Метод для загрузки всех агентов
    :return: Словарь с названием и классом агентов
    """
    agents = {}
    for agent_name, agent_path in Config.AGENTS_TO_LOAD.items():
        module_name, class_name = agent_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        agent_class = getattr(module, class_name)
        agents[agent_name] = agent_class()
    return agents