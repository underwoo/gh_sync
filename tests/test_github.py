import github
import pytest

from . import read_config

config = read_config.getConfig()

gh_test_group = "NOAA-GFDL"

def test_github():
    """This test will test the connection to the GitHub API using a
    access token.  The return should be a GitHub object.
    """
    gh = github.Github(config['GHtoken'])
    assert isinstance(gh, github.Github)


def test_getRepos():
    """This test will get all the repositories from the test GitHub
    organization.
    The return should be a list of repositories.
    """
    gh = github.Github(config['GHtoken'])
    repos = gh.getRepos(gh_test_group, "orgs")
    print(f"Got type {type(repos)}")
    assert isinstance(repos, list)
    print(f"Got list of size {len(repos)}")
    assert len(repos) > 0
    # All returned repositories should be a GithubProject object,
    # and have a non-zero ID
    for repo in repos:
        print(f"Repo is of type {type(repo)}")
        assert isinstance(repo, github.github.GithubRepo)
        assert(f"Repo ID is {repo.id}")
        assert repo.id > 0


def test_getRepo_badowner():
    """This test will pass a bad owner type.
    The result should be an exception"""
    gh = github.Github(config['GHtoken'])
    with pytest.raises(github.github.OwnerTypeError) as errinfo:
        repos = gh.getRepos(gh_test_group, "bad")
    assert str(errinfo.value) == ": Unknown GitHub owner type: 'bad'"
