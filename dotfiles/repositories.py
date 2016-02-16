from .repository import Repository


DEFAULT_IGNORE_PATTERNS = ['README*', '.git', '.hg', '*~']


class Repositories(object):

    def __init__(self, paths, dot):
        self.repos = []
        for path in paths:
            self.repos.append(
                Repository(path,
                           ignore_patterns=DEFAULT_IGNORE_PATTERNS,
                           preserve_leading_dot=dot))

    def __len__(self):
        return len(self.repos)

    def __getitem__(self, index):
        return self.repos[index]
