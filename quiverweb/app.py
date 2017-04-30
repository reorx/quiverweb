#!/usr/bin/env python
# -*- coding: utf-8 -*-

from params.contrib.tornado import use_raw
from torext.app import TorextApp
from torext.handlers import BaseHandler as _BaseHandler
from simplemongo.errors import ObjectNotFound

import settings
from quiverweb.models import Notebook, Note, Resource
from quiverweb.json_helper import encode_json


app = TorextApp(settings)

app.register_json_encoder(encode_json)


class DuplicateObject(Exception):
    pass


class BaseHandler(_BaseHandler):
    pass


@app.route('/api/notebooks')
class NotebooksHandler(BaseHandler):
    def get(self):
        pass

    @use_raw(is_json=True)
    def post(self):
        nb = Notebook(self.params)
        nb_stored = Notebook.one({'id': nb['id']})
        if nb_stored:
            raise DuplicateObject('{} already stored in database'.format(nb['id']))
        nb.save()
        self.write_json(nb)


@app.route('/api/notebooks/([\w-]+)')
class NotebooksItemHandler(BaseHandler):
    def get(self, nb_id):
        nb = Notebook.one_or_raise({'id': nb_id})
        self.write_json(nb)

    @use_raw(is_json=True)
    def put(self, nb_id):
        nb = Notebook.one_or_raise({'id': nb_id})
        Notebook.col.update_one(nb.identifier, self.params)


@app.route('/api/notebooks/index')
class NotebooksIndexHandler(BaseHandler):
    def get(self):
        self.write_json({})


@app.route('/api/notes')
class NotesHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        pass

    def put(self):
        pass


@app.route('/api/notes/index')
class NotesIndexHandler(BaseHandler):
    def get(self):
        self.write_json({})


@app.route('/api/resources')
class ResourcesHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        pass

    def put(self):
        pass


@app.route('/api/resources/index')
class ResourcesIndexHandler(BaseHandler):
    def get(self):
        self.write_json({})


if '__main__' == __name__:
    app.command_line_config()
    app.run()
