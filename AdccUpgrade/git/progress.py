import git
from tqdm import tqdm


class GitProgress(git.remote.RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm()

    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.desc = f"{self.op_code2string(op_code)} : {message}"
        self.pbar.refresh()
        if self.op_code2string(op_code) == 'completed':
            self.pbar.close()

    def op_code2string(self, op_code):
        if op_code == 5:
            return "starting"
        if op_code == git.remote.RemoteProgress.BEGIN:
            return "starting"
        if op_code == git.remote.RemoteProgress.CHECKING_OUT:
            return "checking"
        if op_code == git.remote.RemoteProgress.COUNTING:
            return "counting"
        if op_code == git.remote.RemoteProgress.DONE_TOKEN:
            return "done"
        if op_code == git.remote.RemoteProgress.FINDING_SOURCES:
            return "finding resources"
        if op_code == git.remote.RemoteProgress.RECEIVING:
            return "receiving"
        if op_code == git.remote.RemoteProgress.STAGE_MASK:
            return "stage mask"
        if op_code == git.remote.RemoteProgress.END:
            return "end"
        if op_code == git.remote.RemoteProgress.OP_MASK:
            return "op mask"
        if op_code == git.remote.RemoteProgress.COMPRESSING:
            return "compressing"
        if op_code == git.remote.RemoteProgress.WRITING:
            return "writing"
        if op_code == git.remote.RemoteProgress.RESOLVING:
            return "resolving"
        if op_code == 66:
            return "completed"

        return "undefined"
