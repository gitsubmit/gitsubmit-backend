import os
import subprocess

__author__ = 'shawkins'
"""
Yes, this filename does not comply with PEP8. Thank robotframework for that.
"""

class LocalActionsLib(object):

    def clone_repo(self, repo_name, working_dir, as_teacher=True):
        if as_teacher:
            git_host = "test_gitsubmit_repo_as_teacher"
        else:
            git_host = "test_gitsubmit_repo_as_student"
        process = subprocess.Popen("git clone " + git_host + ":" + repo_name, shell=True, cwd=working_dir,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        print out, err
        print os.environ

    def clone_known_project(self, working_dir):
        self.clone_repo("test_class/test_project", working_dir=working_dir, as_teacher=True)

    def known_project_should_exist(self, working_dir):
        full_path = os.path.join(working_dir, "test_project")
        if not os.path.exists(full_path):
            raise Exception("Path "+str(full_path)+" does not exist!")
