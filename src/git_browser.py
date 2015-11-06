import os
import subprocess
from config import STATIC_REPOS_ROOT
from git import Repo
from git import Git

__author__ = 'shawkins'


class RepoDoesNotExistError(Exception): pass


class GitRepo(object):

    def __init__(self, full_uri):

        STATIC_REPOS_ROOT = ""

        repo_exists = os.path.exists(STATIC_REPOS_ROOT + full_uri)
        self.repo_path = os.path.abspath(STATIC_REPOS_ROOT + full_uri)
        if not repo_exists:
            raise RepoDoesNotExistError(str(STATIC_REPOS_ROOT + full_uri) + " could not be found on this server!")
        self.repo = Repo(self.repo_path)
        self.git = Git(self.repo_path)

    def get_file_or_directory(self, commit_or_branch, path):
        # Incomplete method 1
        if commit_or_branch in self.repo.branches:
            commit = self.repo.branches[commit_or_branch].commit
        else:
            commit = self.repo.commit(commit_or_branch)
        tree = commit.tree
        file = tree[path]

        print file.data_stream.read()

        # complete but not as good method 2
        commit_string = commit.hexsha
        callpipe = subprocess.Popen("git show "+commit_string+":"+path, shell=True, cwd=self.repo_path,
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = callpipe.communicate()
        if out.startswith("tree "+commit_string):
            print "this is a directory"
        else:
            print "this is a file"
        print out
g = GitRepo("/Users/shawkins/Code/gitsubmit")
g.get_file_or_directory("f94e9fb83424", "src/config.py")