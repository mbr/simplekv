from io import BytesIO
import re
import time

from dulwich.repo import Repo
from dulwich.objects import Commit, Tree, Blob

from . import KeyValueStore, __version__


def _on_tree(repo, tree, components, obj):
    """Mounts an object on a tree, using the given path components.

    :param tree: Tree object to mount on.
    :param components: A list of strings of subpaths (i.e. ['foo', 'bar'] is
                       equivalent to '/foo/bar')
    :param obj: Object to mount. If None, removes the object found at path
                and prunes the tree downwards.
    :return: A list of new entities that need to be added to the object store,
             where the last one is the new tree.
    """

    # pattern-matching:
    if len(components) == 1:
        if isinstance(obj, Blob):
            mode = 0o100644
        elif isinstance(obj, Tree):
            mode = 0o040000
        elif obj is None:
            mode = None
        else:
            raise TypeError('Can only mount Blobs or Trees')
        name = components[0]

        if mode is not None:
            tree[name] = mode, obj.id
            return [tree]
        if name in tree:
            del tree[name]
        return [tree]
    elif len(components) > 1:
        a, bc = components[0], components[1:]
        if a in tree:
            a_tree = repo[tree[a][1]]
            if not isinstance(a_tree, Tree):
                a_tree = Tree()
        else:
            a_tree = Tree()
        res = _on_tree(repo, a_tree, bc, obj)
        a_tree_new = res[-1]

        if a_tree_new.items():
            tree[a] = 0o040000, a_tree_new.id
            return res + [tree]

        # tree is empty
        if a in tree:
            del tree[a]
        return [tree]
    else:
        raise ValueError('Components can\'t be empty.')


class GitCommitStore(KeyValueStore):
    AUTHOR = 'GitCommitStore (simplekv {}) <>'.format(__version__)
    TIMEZONE = None

    def __init__(self, repo_path, branch=b'master', subdir=b''):
        self.repo = Repo(repo_path)
        self.branch = branch

        # cleans up subdir, to a form of 'a/b/c' (no duplicate, leading or
        # trailing slashes)
        self.subdir = re.sub('#/+#', '/', subdir.decode('ascii').strip('/'))

    @property
    def _subdir_components(self):
        return [c.encode('ascii') for c in self.subdir.split('/')]

    @property
    def _refname(self):
        return b'refs/heads/' + self.branch

    def _create_top_commit(self):
        # get the top commit, create empty one if it does not exist
        commit = Commit()

        # commit metadata
        author = self.AUTHOR.encode('utf8')
        commit.author = commit.committer = author
        commit.commit_time = commit.author_time = int(time.time())

        if self.TIMEZONE is not None:
            tz = self.TIMEZONE
        else:
            tz = time.timezone if (time.localtime().tm_isdst) else time.altzone
        commit.commit_timezone = commit.author_timezone = tz
        commit.encoding = b'UTF-8'

        return commit

    def _delete(self, key):
        try:
            commit = self.repo[self._refname]
            tree = self.repo[commit.tree]
        except KeyError:
            return  # not-found key errors are ignored

        commit = self._create_top_commit()
        objects_to_add = []

        components = [key.encode('ascii')]
        if self.subdir:
            components = self._subdir_components + components

        res = _on_tree(self.repo, tree, components, None)
        objects_to_add.extend(res)
        tree = res[-1]

        commit.tree = tree.id
        commit.message = (
            'Deleted key {}'.format(self.subdir + '/' + key)).encode('utf8')

        objects_to_add.append(commit)

        for obj in objects_to_add:
            self.repo.object_store.add_object(obj)

        self.repo.refs[self._refname] = commit.id

    def _get(self, key):
        # might raise key errors, except block corrects param
        try:
            commit = self.repo[self._refname]
            tree = self.repo[commit.tree]
            fn = self.subdir + '/' + key
            _, blob_id = tree.lookup_path(self.repo.__getitem__,
                                          fn.encode('ascii'))
            blob = self.repo[blob_id]
        except KeyError:
            raise KeyError(key)

        return blob.data

    def iter_keys(self):
        try:
            commit = self.repo[self._refname]
            tree = self.repo[commit.tree]

            if self.subdir:
                tree = self.repo[tree.lookup_path(
                    self.repo.__getitem__, self.subdir.encode('ascii'))[1]]
        except KeyError:
            pass
        else:
            for name in tree:
                yield name.decode('ascii')

    def _open(self, key):
        return BytesIO(self._get(key))

    def _put_file(self, key, file):
        # FIXME: it may be worth to try to move large files directly into the
        #        store here
        return self._put(key, file.read())

    def _put(self, key, data):
        commit = self._create_top_commit()
        commit.message = (
            'Updated key {}'.format(self.subdir + '/' + key)).encode('utf8')

        blob = Blob.from_string(data)

        try:
            parent_commit = self.repo[self._refname]
        except KeyError:
            # branch does not exist, start with an empty tree
            tree = Tree()
        else:
            commit.parents = [parent_commit.id]
            tree = self.repo[parent_commit.tree]

        objects_to_add = [blob]

        # no subdirs in filename, add directly to tree
        components = [key.encode('ascii')]
        if self.subdir:
            components = self._subdir_components + components
        res = _on_tree(self.repo, tree, components, blob)
        objects_to_add.extend(res)

        commit.tree = res[-1].id
        objects_to_add.append(commit)

        # add objects
        for obj in objects_to_add:
            self.repo.object_store.add_object(obj)

        # update refs
        self.repo.refs[self._refname] = commit.id

        return key
