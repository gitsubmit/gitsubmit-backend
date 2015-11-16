import binascii
import os
import datetime
import requests
from SSHKeyLib import SSHKeyLib

__author__ = 'shawkins'
"""
Yes, this filename does not comply with PEP8. Thank robotframework for that.
"""

class APIClientLib(object):

    def make_request(self, method_callback, url, data=None, is_json=True, include_headers=False):
        print "making "+str(method_callback)+" request to "+str(url)
        if data:
            print "sending data: "
            print data
        result = method_callback(url, data=data)
        if is_json:
            result_obj = result.json()
        else:
            result_obj = result.text
        return_obj = {"status_code": result.status_code,
                      "data": result_obj}
        if include_headers:
            return_obj["headers"] = result.headers
        print "data retrieved: "
        print return_obj
        return return_obj

    def update_due_date(self, url_root, class_name, project_name, new_due_date):
        updated_date_obj = {"date": new_due_date}
        url = url_root+"/classes/"+class_name+"/projects/"+project_name+"/due_date/"
        method_cb = requests.post
        return self.make_request(method_cb, url, updated_date_obj)

    def create_predefined_project(self, url_root, class_name):
        randomized_url_name = "test_predefined_project"
        long_name = "A Predefined Project for Testing"
        project_obj = {"url_name": randomized_url_name, "project_name": long_name, "description": long_name,
                       "team_based": True, "max_members": 4,
                       "due_date": (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")}
        url = url_root+"/classes/" + class_name +"/projects/"
        method_cb = requests.post
        return self.make_request(method_cb, url, project_obj)

    def create_randomized_project(self, url_root, class_name):
        randomized_url_name = "test_random_project_" + binascii.b2a_hex(os.urandom(15))[:8]
        long_name = "A Randomized Project for Testing"
        project_obj = {"url_name": randomized_url_name, "project_name": long_name, "description": long_name,
                       "team_based": True, "max_members": 4,
                       "due_date": (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")}
        url = url_root+"/classes/" + class_name +"/projects/"
        method_cb = requests.post
        return self.make_request(method_cb, url, project_obj)

    def get_project_individually(self, url_root, class_name, project_name):
        url = url_root+"/classes/"+class_name+"/projects/"+project_name+"/"
        method_cb = requests.get
        return self.make_request(method_cb, url)

    def get_project_owner(self, url_root, class_name, project_name):
        url = url_root+"/classes/"+class_name+"/projects/"+project_name+"/owner/"
        method_cb = requests.get
        return self.make_request(method_cb, url)

    def add_teacher_to_class(self, url_root, teacher, class_name):
        url = url_root+"/classes/"+class_name+"/teacher/"
        method_cb = requests.post
        teacher_obj = {"username": teacher}
        return self.make_request(method_cb, url, teacher_obj)

    def get_class_owner(self, url_root, class_name):
        url = url_root+"/classes/"+class_name+"/owner/"
        method_cb = requests.get
        return self.make_request(method_cb, url)

    def get_class_individually(self, url_root, class_name):
        url = url_root+"/classes/"+class_name+"/"
        method_cb = requests.get
        return self.make_request(method_cb, url)

    def get_class_projects(self, url_root, class_name):
        url = url_root+"/classes/"+class_name+"/projects/"
        method_cb = requests.get
        return self.make_request(method_cb, url)

    def get_class_teachers(self, url_root, class_name):
        url = url_root+"/classes/"+class_name+"/teachers/"
        method_cb = requests.get
        return self.make_request(method_cb, url)

    def enroll_student_in_class(self, url_root, student, class_name):
        url = url_root+"/classes/"+class_name+"/student/"
        method_cb = requests.post
        student_obj = {"username": student}
        return self.make_request(method_cb, url, student_obj)

    def list_students_in_class(self, url_rool, class_name):
        url = url_rool+"/classes/"+class_name+"/students/"
        method_cb = requests.get
        return self.make_request(method_cb, url)

    def list_classes(self, url_root):
        url = url_root+"/classes/"
        method_cb = requests.get
        return self.make_request(method_cb, url)

    def create_randomized_class(self, url_root):
        randomized_url_name = "test_random_class_" + binascii.b2a_hex(os.urandom(15))[:8]
        long_name = "A Randomized Class for Testing"
        url = url_root+"/classes/"
        method_cb = requests.post
        class_obj = {"url_name": randomized_url_name, "class_name": long_name, "description": long_name}
        return self.make_request(method_cb, url, class_obj)

    def get_submission_individually(self, url_root, owner, submission):
        url = url_root+"/" + owner + "/submissions/" + submission
        method_cb = requests.get
        return self.make_request(method_cb, url)

    def create_predefined_class(self, url_root):
        randomized_url_name = "test_predef_classs"
        long_name = "A Predefined Class for Testing"
        url = url_root+"/classes/"
        method_cb = requests.post
        class_obj = {"url_name": randomized_url_name, "class_name": long_name, "description": long_name}
        return self.make_request(method_cb, url, class_obj)

    def list_keys_for_user(self, url_root, user):
        url = url_root+"/"+user+"/ssh_keys/"
        method_cb = requests.get
        return self.make_request(method_cb, url)

    def add_randomized_key_to_user(self, url_root, user):
        ssh = SSHKeyLib()
        key = ssh.create_bogus_key()["pubkey_contents"]
        key_obj = {"pkey_contents": key}
        url = url_root+"/"+user+"/ssh_keys/"
        method_cb = requests.post
        return self.make_request(method_cb, url, key_obj)

    def add_preset_key1_to_user(self, url_root, user):
        preset_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCqNP8fAI3WnE5zOjWPtJU3zSE7Dbm1x9qwY28DqXs+0s6UFjSc0WOGY5wsXUkzjgXK0U3TfAyiZOu7CAbQfWIpxTODjAu9UqRxMgGzWh/i/CO+uYrgb7hgVfXycyzrMHfKrA6vW7WjBQ2qfFz1GnVhXuvDMWlKROgTj/GvmGtVQz1olA9drvfcDE+z1+lT0moe4C/IFr7T3j6YROVEge6WvOD0Zxzj2awZ2SbLxdeup29AbOp4tbRC8qAK6cZWjkBRixyAiZ4yEsNr/CcM6Y/jpHuu6iCM59EtWFSEiujCcf1JRYaMbHVC4eqpwldwJy6c1lpfNULnS9aIQT8NNSGj shawkins@rrcs-97-77-50-220.sw.biz.rr.com"
        key_obj = {"pkey_contents": preset_key}
        url = url_root+"/"+user+"/ssh_keys/"
        method_cb = requests.post
        return self.make_request(method_cb, url, key_obj)

    def add_preset_key2_to_user(self, url_root, user):
        preset_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDPISQ/uPxmzg1/bTbu16eyU+hGrR/MdJKNDgIh6X7OohSIfDyrfXgt3vz36VO6DaF94gV9Z+uRI+/JQsSfzg3r8LUt3JU9DFd5flxm01nknqYNyPF09uKXdcGr4SfmQ54hM0tq4/5NS0wkRRFbOplcvtDa3ZjXEmoFKAzXfxbknH+BkgBksjwL4L8m4o7ZxP21CHkAU8bfJDwjVdxtPhMiCQKqmsfj8P3ARTDj/e4CJmWrRaz9Xw4QMKDemkhzmJB/f0vjAmM3H7GzEsVsDTkNweHdDubp7Tynx5+QKv2iqZvgNJGA+ahcqJ/IUUtEPsAFFK5Hy6YOO4GT4nnZkOsD shawkins@rrcs-97-77-50-220.sw.biz.rr.com"
        key_obj = {"pkey_contents": preset_key}
        url = url_root+"/"+user+"/ssh_keys/"
        method_cb = requests.post
        return self.make_request(method_cb, url, key_obj)

    def remove_key_from_user(self, url_root, user, key_to_remove):
        request_obj = {"pkey": key_to_remove}
        url = url_root+"/"+user+"/ssh_keys/"
        method_cb = requests.delete
        return self.make_request(method_cb, url, request_obj)

    def user_removes_all_but_one_key(self, url_root, user):
        keys_obj = self.list_keys_for_user(url_root, user)
        for key in keys_obj["data"]["keys"][1:]:
            self.remove_key_from_user(url_root, user, key)

    def get_project_file_or_dir_from_api(self, url_root, class_name, project_name, commit_or_branch, filepath):
        url = url_root + "/classes/" + class_name + "/projects/" + project_name + "/source/" + commit_or_branch + "/" + filepath
        method_cb = requests.get
        return self.make_request(method_cb, url, is_json=False, include_headers=True)

    def get_users_landing_page(self, url_root, user):
        url = url_root + "/" + user + "/landing/"
        method_cb = requests.get
        return self.make_request(method_cb, url)
