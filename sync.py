# coding: utf-8

import os
import json
import logging


NOTEBOOK_KEYS = ['name', 'uuid']

NOTE_KEYS = ['uuid', 'title', 'cells', 'tags', 'created_at', 'updated_at']

lg = logging.getLogger('quiverweb.sync')


def get_change_list(quiver_path, remote_notebooks_index, remote_notes_index):
    """
    remote_notebooks_index = {
        'Inbox': 1452326207,
        'CAFA2902-F309-4D2B-BFC0-D6B8C0A12DB6': 1452326207,
    }

    remote_notes_index = {
        '02FEC1AA-AB0E-4686-B54D-50D87AD7C4A1': 1452326207,
    }

    change_list = {
        'notebook': {
            'create': [],
            'update': [],
            'delete': [],
        },
        'note': {
            'create': [],
            'update': [],
            'delete': [],
        }
    }
    """
    def _path(*args):
        return reduce(lambda x, y: os.path.join(x, y), [quiver_path] + list(args))

    notebooks, notebooks_dict = get_notebooks(quiver_path)
    #print 'notebooks_dict', notebooks_dict

    notes = []
    notes_dict = {}
    for nb in notebooks:
        _notes, _notes_index = get_notebook_notes(nb)
        notes += _notes
        notes_dict.update(_notes_index)
    #print 'notes_dict', notes_dict

    change_list = {
        'notebook': get_changes(notebooks_dict, remote_notebooks_index),
        'note': get_changes(notes_dict, remote_notes_index),
    }

    change_list_summary = {
        k: {_k: len(_v) for _k, _v in changes.iteritems()}
        for k, changes in change_list.iteritems()
    }
    lg.info('change_list summary: \n%s', json.dumps(change_list_summary, indent=4))

    return change_list


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
    l = []
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

        l.append(nb)
        d[nb['id']] = nb

    return l, d


def get_notebook_notes(notebook):
    def _path(*args):
        return reduce(lambda x, y: os.path.join(x, y), [notebook['path']] + list(args))

    root, dirs, files = os.walk(notebook['path']).next()
    l = []
    d = {}
    for dir in dirs:
        note = get_file_content(_path(dir, 'content.json'), as_json=True)
        note.update(get_file_content(_path(dir, 'meta.json'), as_json=True))

        check_dict_keys(note, NOTE_KEYS)

        # add `notebook_id`
        note.update(
            notebook_id=notebook['id']
        )

        # move `uuid` -> `id`
        note['id'] = note.pop('uuid')

        l.append(note)
        d[note['id']] = note

    return l, d


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


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    quiver_path = '/Users/reorx/Dropbox/Library/Quiver.qvlibrary'

    get_change_list(quiver_path, {}, {})
