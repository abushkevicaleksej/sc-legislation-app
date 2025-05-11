from json import JSONEncoder

from sc_client.models import ScTemplate, ScAddr

class SCJSONEncoder(JSONEncoder):
    def default(self, obj):
        print(f"Serializing: {type(obj)}")  # Отладочный вывод
        if isinstance(obj, ScAddr):
            return obj.value
        return super().default(obj)