# coding: utf-8

import pymongo
from simplemongo import Document
from . import settings

db = pymongo.MongoClient(settings.MONGODB_URI)[settings.MONGODB_NAME]


class Notebook(Document):
    """
    {
        "id": "771CA538-9C64-4B93-BA32-A0DC106EE2F5",
        "name": "Thoughts",
        "created_at": 1452326218,
        "updated_at": 1452326218
    }
    """
    col = db['notebooks']

    # Enable validation on writing the document
    __validate__ = True

    struct = {
        'id': str,
        'name': str,
        'created_at': int,
        'updated_at': int,
    }


class Note(Document):
    """
    {
        "id": "DE053C13-33F0-4483-9A13-F38B50A2F04E",
        "notebook_id": "78C0EDB1-B8B8-448A-81A5-53FDEFFB06D8",
        "title": "tcpdump & network analyzing",
        "cells": [
            {
                "data": "",
                "type": "markdown"
            },
        ],
        "tags": [],
        "resources": {},
        "created_at": 1458289488,
        "updated_at": 1458290046
    }
    """
    col = db['notes']

    __validate__ = True

    struct = {
        'id': str,
        'notebook_id': str,
        'title': str,
        'cells': list,
        'tags': list,
        'resources': dict,
        'created_at': int,
        'updated_at': int,
    }


class Resource(Document):
    """
    {
        "id": "2F3FFAE3A094F0D679D02D71AE0560BA",
        "ext": "jpg",
        "created_at": 1455946806,
        "updated_at": 1455946799
    }
    """
    col = db['resources']

    __validate__ = True

    struct = {
        'id': str,
        'ext': str,
        'created_at': int,
        'updated_at': int,
    }
