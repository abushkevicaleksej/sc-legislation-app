from json import JSONEncoder

from sc_client.models import ScTemplate, ScAddr

class SCJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ScAddr):
            return obj.value
        return super().default(obj)