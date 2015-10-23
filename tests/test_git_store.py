from basic_store import BasicStore
from dulwich.repo import Repo
from idgens import UUIDGen, HashGen
from tempdir import TempDir
import pytest

from simplekv.git import GitCommitStore

# FIXME: test subdir support


class TestGitCommitStore(BasicStore, UUIDGen, HashGen):
    @pytest.fixture(params=['master', 'not-master', 'other-branch'])
    def branch(self, request):
        return request.param

    @pytest.yield_fixture
    def repo_path(self):
        with TempDir() as tmpdir:
            Repo.init_bare(tmpdir)
            yield tmpdir

    @pytest.fixture
    def store(self, repo_path, branch):
        return GitCommitStore(repo_path, branch=branch)
