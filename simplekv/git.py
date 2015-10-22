from io import BytesIO
import time

from dulwich.repo import Repo
from dulwich.objects import Commit, Tree, Blob

from . import KeyValueStore, __version__


class GitCommitStore(KeyValueStore):
    AUTHOR = 'GitCommitStore (simplekv {})'.format(__version__)
    TIMEZONE = None

    def __init__(self, repo_path, branch=b'master', subdir=b''):
        self.repo = Repo(repo_path)
        self.branch = branch
        self.subdir = subdir

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
            del tree[key.encode('ascii')]
        except KeyError:
            return  # not-found key errors are ignored

        commit = self._create_top_commit()
        commit.tree = tree.id
        commit.message = ('Deleted key {!r}'.format(key)).encode('utf8')

        self.repo.object_store.add_object(tree)
        self.repo.object_store.add_object(commit)

        self.repo.refs[self._refname] = commit.id

    def _get(self, key):
        # might raise key errors, except block corrects param
        try:
            commit = self.repo[self._refname]
            tree = self.repo[commit.tree]
            _, blob_id = tree[key.encode('ascii')]
            blob = self.repo[blob_id]
        except KeyError:
            raise KeyError(key)

        return blob.data

    def iter_keys(self):
        try:
            commit = self.repo[self._refname]
            tree = self.repo[commit.tree]
        except KeyError:
            pass
        else:
            for name in tree:
                yield name.decode('ascii')

    def _open(self, key):
        return BytesIO(self._get(key))

    def _put_file(self, key, file):
        commit = self._create_top_commit()
        commit.message = ('Updated key {!r}'.format(key)).encode('utf8')

        # prepare blob
        if hasattr(file, 'read'):
            buf = file.read()
        else:
            with open(file, 'rb') as fp:
                buf = fp.read()
        blob = Blob.from_string(buf)

        try:
            parent_commit = self.repo[self._refname]
        except KeyError:
            # branch does not exist, start with an empty tree
            tree = Tree()
        else:
            commit.parents = [parent_commit.id]
            tree = self.repo[parent_commit.tree]

        subtree = tree

        # no subdirs in filename, add directly to tree
        subtree.add(key.encode('ascii'), 0o100644, blob.id)

        commit.tree = tree.id

        # add objects
        self.repo.object_store.add_object(blob)
        self.repo.object_store.add_object(tree)
        self.repo.object_store.add_object(commit)

        # update refs
        self.repo.refs[self._refname] = commit.id

        return key
