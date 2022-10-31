
from json import JSONEncoder
import json
from enum import Enum

from dns import models
import cherrypy
import re
import pprint as pp


# Decorator that receives a CLS to encode the json
def json_out(cls):
    def json_out_wrapper(func):
        def inner(*args, **kwargs):
            object_to_be_serialized = func(*args, **kwargs)
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps(object_to_be_serialized, cls=cls).encode("utf-8")

        return inner

    return json_out_wrapper


class NestedEncoder(JSONEncoder):
    def default(self, obj):
        # If it is a class we created and it is having trouble using json_dumps use our to_json class
        if hasattr(obj, "to_json"):
            return obj.to_json()
        # If it is a subclass of Enum just call the name value
        elif isinstance(obj, Enum):
            return obj.name
        else:
            return json.JSONEncoder.default(self, obj)



