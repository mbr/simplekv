Git-based stores
****************

.. warning:: The git-based store here passes all tests, but may perform slower
             than expected. The code should be considered beta quality in this
             release.

The functionality in this module requires the dulwich_ module (but no git
binary). Repositories are manipulated directly, i.e. possibly existing working
copies are not touched.

.. _dulwich: http://dulwich.io

.. class:: simplekv.git.GitCommitStore(repo_path, branch=b'master',\
           subdir=b'')

    A git-commit based store.

    For every put or delete operation, a new commit will be created in a
    git repository. Keys themselves will map onto file-paths in the
    repository, possibly in a subdirectory.

    :param repo_path: Path to the git repository.
    :param branch: The branch to commit to. Must be an ascii-encoded binary
                   string.
    :param subdir: Prefixed to every key committed. Must be an ascii-encoded
                   binary string.
