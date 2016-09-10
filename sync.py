# coding: utf-8

from __future__ import print_function

import os
import json
import logging
import logging.config

import requests


NOTEBOOK_KEYS = ['name', 'uuid']

NOTE_KEYS = ['uuid', 'title', 'cells', 'tags', 'created_at', 'updated_at']

lg = logging.getLogger('quiverweb.sync')


class Env(object):
    prefix = 'QUIVERWEB'
    _instances = {}

    def __init__(self, key, default=None, allow_null=False):
        self.key = key.format(prefix=self.prefix)
        self.default = default
        self.allow_null = allow_null
        Env._instances[self.key] = self

    def get(self):
        v = os.environ.get(self.key, self.default)
        if not self.allow_null and not v:
            raise ValueError('No value for {} is not allowed'.format(self.key))
        return v


class envs:  # NOQA
    LIBRARY_PATH = Env('{prefix}_LIBRARY_PATH')
    API_URL = Env('{prefix}_API_URL')
    LOG_LEVEL = Env('{prefix}_LOG_LEVEL', 'INFO')


class RequestError(Exception):
    pass


class WebAPI(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def _url(self, uri):
        return self.base_url + uri

    def request(self, method, uri, *args, **kwargs):
        request_func = getattr(requests, method.lower())
        url = self._url(uri)
        try:
            resp = request_func(url, *args, **kwargs)
        except requests.exceptions.RequestException as e:
            raise RequestError(str(e))
        if resp.status_code > 299:
            raise RequestError('request error: {}, {}'.format(resp.status_code, resp.content))

        if resp.content:
            return resp.json()
        else:
            return None

    def get_notebooks_index(self):
        d = self.request('get', '/notebooks/index')
        return d

    def get_notes_index(self):
        d = self.request('get', '/notes/index')
        return d

    def get_resources_index(self):
        d = self.request('get', '/resources/index')
        return d

    def post_notebooks_sync(self, changes):
        d = self.request('post', '/notebooks/sync', json=changes)
        return d

    def post_notes_sync(self, changes):
        d = self.request('post', '/notes/sync', json=changes)
        return d

    def post_resource(self, rs):
        d = self.request('post', '/resources', json=rs)
        return d

    def put_resource(self, rs):
        d = self.request('put', '/resources/{}'.format(rs['id']), json=rs)
        return d

    def delete_resource(self, rs_id):
        d = self.request('delete', '/resources/{}'.format(rs_id))
        return d


def get_all_changes(quiver_path, remote_notebooks_index, remote_notes_index, remote_resources_index):
    """
    remote_notebooks_index = {
        'Inbox': 1452326207,
        'CAFA2902-F309-4D2B-BFC0-D6B8C0A12DB6': 1452326207,
    }

    remote_notes_index = {
        '02FEC1AA-AB0E-4686-B54D-50D87AD7C4A1': 1452326207,
    }

    all_changes = {
        'notebook': {
            'create': [],
            'update': [],
            'delete': [],
        },
        'note': {
            'create': [],
            'update': [],
            'delete': [],
        },
        'resource': {
            'create': [],
            'update': [],
            'delete': [],
        }
    }
    """
    def _path(*args):
        return reduce(lambda x, y: os.path.join(x, y), [quiver_path] + list(args))

    notebooks_dict = get_notebooks(quiver_path)
    lg.debug('notebook data: %s', json.dumps(notebooks_dict.values()[0]))

    notes_dict = {}
    resources_dict = {}

    for nb in notebooks_dict.itervalues():
        _notes_dict = get_notebook_notes(nb)
        notes_dict.update(_notes_dict)

        for n in _notes_dict.itervalues():
            resources_dict.update(n['resources'])

    lg.debug('note data: %s', json.dumps(notes_dict.values()[0]))
    lg.debug('resource data: %s', json.dumps(resources_dict.values()[0]))

    all_changes = {
        'notebook': get_changes(notebooks_dict, remote_notebooks_index),
        'note': get_changes(notes_dict, remote_notes_index),
        'resource': get_changes(resources_dict, remote_resources_index),
    }

    all_changes_summary = {
        k: {_k: len(_v) for _k, _v in changes.iteritems()}
        for k, changes in all_changes.iteritems()
    }
    lg.info('all_changes summary: \n%s', json.dumps(all_changes_summary, indent=4))

    return all_changes


def get_changes(local_dict, remote_index):
    changes = {
        'create': [],
        'update': [],
        'delete': [],
    }

    for i in local_dict:
        item = local_dict[i]
        if i in remote_index:
            # update
            if item['updated_at'] != remote_index[i]:
                changes['update'].append(item)
        else:
            # create
            changes['create'].append(item)

    for i in remote_index:
        if i not in local_dict:
            # delete
            changes['delete'].append(i)

    return changes


def get_notebooks(quiver_path):
    def _path(*args):
        return reduce(lambda x, y: os.path.join(x, y), [quiver_path] + list(args))

    root, dirs, files = os.walk(quiver_path).next()
    d = {}
    for dir in dirs:
        metapath = _path(dir, 'meta.json')
        nb = get_file_content(metapath, as_json=True)

        check_dict_keys(nb, NOTEBOOK_KEYS)

        # add `created_at`, `updated_at`
        stat = get_file_stat(metapath)
        nb.update(
            created_at=stat['st_ctime'],
            updated_at=stat['st_mtime'],
        )

        # add `path`
        nb.update(
            path=_path(dir)
        )

        # move `uuid` -> `id`
        nb['id'] = nb.pop('uuid')

        d[nb['id']] = nb

    return d


def get_notebook_notes(notebook):
    def _path(*args):
        return reduce(lambda x, y: os.path.join(x, y), [notebook['path']] + list(args))

    _r, dirs, _f = os.walk(notebook['path']).next()
    d = {}
    for dir in dirs:
        note_path = os.path.join(notebook['path'], dir)

        note = get_file_content(_path(dir, 'content.json'), as_json=True)
        note.update(get_file_content(_path(dir, 'meta.json'), as_json=True))

        check_dict_keys(note, NOTE_KEYS)

        # add `notebook_id`
        note.update(
            notebook_id=notebook['id']
        )

        # move `uuid` -> `id`
        note['id'] = note.pop('uuid')

        # add `resources`
        resources = {}
        resources_path = os.path.join(note_path, 'resources')
        if os.path.exists(resources_path):
            _r, _d, resource_files = os.walk(resources_path).next()
            for name in resource_files:
                rs_id, rs_ext = tuple(name.split('.'))
                rs_stat = get_file_stat(os.path.join(resources_path, name))
                rs = {
                    'id': rs_id,
                    'ext': rs_ext,
                    'created_at': rs_stat['st_ctime'],
                    'updated_at': rs_stat['st_mtime'],
                }
                resources[rs_id] = rs
        note['resources'] = resources

        d[note['id']] = note

    return d


def get_file_content(filepath, as_json=False):
    with open(filepath, 'r') as f:
        content = f.read()
    if as_json:
        return json.loads(content)
    else:
        return content


def get_file_stat(filepath):
    stat = os.stat(filepath)
    d = {}
    for i in ['st_mtime', 'st_ctime']:
        v = getattr(stat, i)
        if i.endswith('time'):
            v = int(v)
        d[i] = v
    return d


def check_dict_keys(d, keys):
    for i in keys:
        if i not in d:
            raise KeyError('Key {} not in dict: {}'.format(i, d))


def setup_logging(level):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'loggers': {
            '': {
                'handlers': ['stream'],
                'level': level,
            },
            'requests': {
                'level': 'DEBUG',
            }
        },
        'handlers': {
            'stream': {
                'class': 'logging.StreamHandler',
                'formatter': 'common',
            },
        },
        'formatters': {
            'common': {
                'format': '%(asctime)s %(levelname)s %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
    })


def main():
    print('Envs:\n' + '\n'.join('  ' + k for k in Env._instances))

    library_path = envs.LIBRARY_PATH.get()
    api_url = envs.API_URL.get()
    log_level = envs.LOG_LEVEL.get()

    setup_logging(log_level)

    api = WebAPI(api_url)

    notebooks_index = api.get_notebooks_index()
    notes_index = api.get_notes_index()
    resources_index = api.get_resources_index()

    get_all_changes(library_path, notebooks_index, notes_index, resources_index)


if __name__ == '__main__':
    main()
