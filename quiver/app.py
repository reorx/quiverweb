#!/usr/bin/env python
# -*- coding: utf-8 -*-

from torext.app import TorextApp
from torext.handlers import BaseHandler
import settings


app = TorextApp(settings)


@app.route('/api/notebooks')
class NotebooksHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        pass

    def put(self):
        pass


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


if '__main__' == __name__:
    app.command_line_config()
    app.run()
