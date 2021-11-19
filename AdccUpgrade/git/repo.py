from git import Repo
from pathlib import Path
from AdccUpgrade.param import BaseParams
from .progress import GitProgress


def create_git_dict(name='', path='', url='', auto_clone=True):
    return dict(git=dict(name=name, path=path, url=url, auto_clone=auto_clone))


class GitRepo(BaseParams):
    name: str = None
    repo: Repo = None

    def __init__(self, **kw):
        if 'git' not in kw:
            kw.update(**create_git_dict())
        super(GitRepo, self).__init__(**kw)

        if self.params.git.auto_clone:
            if not Path(self.params.git.path).exists() and self.params.git.url != "":
                self.clone()
        self.open()

    def open(self):
        if Path(self.params.git.path).exists():
            self.repo = Repo(self.params.git.path, search_parent_directories=True)
            self.params.git.url = self.extract_url()
            self.save_params()
        else:
            raise GitRepoOpenPathNotExist(self)

    def clone(self):
        if self.params.git.url != '':
            self.repo = Repo.clone_from(self.params.git.url, self.params.git.path, branch='develop',
                                        progress=GitProgress())
        else:
            raise GitRepoCloneButTheUrlIsNotSet(self, 'clone')

    def git_action(self, action, *args):
        if self.repo is None:
            raise GitRepoActionWhereRepoIsNone(self, action)

        if not hasattr(self.repo.git, action):
            raise GitRepoGitActionGitNotExist(self, action)
        # Get Action Fx pointer
        opt = getattr(self.repo.git, action)
        # Call action with args
        output = str(opt(args)).replace('\n', ' ')
        return output

    def extract_url(self):
        if self.repo:
            return list(self.repo.remote().urls)[0]

    def create_tag(self, tag):
        if self.repo is None:
            raise (self, tag)
        return self.repo.create_tag(tag)

    def checkout(self, target):
        return self.git_action('checkout', target)


# Exceptions 1 - ConfigurationFileMustBeUpdated
class GitRepoOpenPathNotExist(Exception):
    def __init__(self, git_repo):
        print(f"[Exception] - Git Repo Open Path Not Exist! -> {git_repo}")


# Exceptions 2 - ConfigurationFileMustBeUpdated
class GitRepoActionWhereRepoIsNone(Exception):
    def __init__(self, git_repo, action: str):
        print(f"[Exception] - {action} - Git Repo Action where Repo is None! -> {git_repo}")


# Exceptions 3 - GitRepoGitActionGitNotExist
class GitRepoGitActionGitNotExist(Exception):
    def __init__(self, git_repo, action: str):
        print(f"[Exception] - {action} - GitRepoGitActionGitNotExist! -> {git_repo}")


# Exceptions 3 - GitRepoGitActionGitNotExist
class GitRepoRepositoryActionGitNotExist(Exception):
    def __init__(self, git_repo, action: str):
        print(f"[Exception] - {action} - GitRepoRepositoryActionGitNotExist! -> {git_repo}")


# Exceptions 4 - GitRepoCloneButTheUrlIsNotSet
class GitRepoCloneButTheUrlIsNotSet(Exception):
    def __init__(self, git_repo, action: str):
        print(f"[Exception] - {action} - GitRepoCloneButTheUrlIsNotSet! -> {git_repo}")
