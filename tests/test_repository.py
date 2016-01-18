import pytest

from dotfiles.repository import Repository


def test_init(repo, home):
    repo.remove()
    assert repo.check(exists=0)

    r = Repository(repo, home)
    assert r.repodir == repo
    assert r.homedir == home
    assert repo.check(exists=1, dir=1)

def test_str(repo, home):
    repo.ensure('.a')
    repo.ensure('.b')
    repo.ensure('.c')

    r = Repository(repo, home)

    assert str(r) == ('%s\n%s\n%s' % (home.join('.a'),
                                      home.join('.b'),
                                      home.join('.c')))

def test_repr(repo):
    actual = '%r' % Repository(repo, None)
    expected = '<Repository local(\'%s\')>' % repo
    assert actual == expected

def test_target_to_name(repo, home):
    actual = Repository(repo, home)._target_to_name(repo.join('.foo'))
    expected = home.join('.foo')
    assert actual == expected

def test_name_to_target(repo, home):
    actual = Repository(repo, home)._name_to_target(home.join('.foo'))
    expected = repo.join('.foo')
    assert actual == expected

@pytest.mark.xfail(reason='TODO')
def test_dotfile():
    assert False

def test_contents(repo, home):

    assert Repository(repo, home).contents() == []

    target_a = repo.ensure('a')
    target_b = repo.ensure('b')
    target_c = repo.ensure('c')
    contents = Repository(repo, home).contents()

    assert contents[0].target == target_a
    assert contents[1].target == target_b
    assert contents[2].target == target_c

def test_nested_name_to_target(repo, home):
    r = Repository(repo, home)

    actual = r._name_to_target(home.join('.vim/.mrconfig'))
    expected = repo.join('.vim/.mrconfig')
    assert actual == expected
