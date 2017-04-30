# coding: utf-8

import json
from json import JSONEncoder
import datetime
from bson.objectid import ObjectId


TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class DocumentJSONEncoder(JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time
    """
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime(TIME_FORMAT)
        if isinstance(o, ObjectId):
            return str(o)
        else:
            return super(DocumentJSONEncoder, self).default(o)


def encode_json(o):
    return json.dumps(o, cls=DocumentJSONEncoder)
