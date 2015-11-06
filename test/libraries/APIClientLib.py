import binascii
import os
import requests
from SSHKeyLib import SSHKeyLib

__author__ = 'shawkins'
"""
Yes, this filename does not comply with PEP8. Thank robotframework for that.
"""

class APIClientLib(object):

    def list_classes(self, url_root):
        classes_result = requests.get(url_root+"/classes/")
        classes_obj = classes_result.json()
        return_obj = {"status_code": classes_result.status_code,
                      "data": classes_obj}
        return return_obj

    def create_randomized_class(self, url_root):
        randomized_url_name = "test_random_class_" + binascii.b2a_hex(os.urandom(15))[:8]
        long_name = "A Randomized Class for Testing"
        class_obj = {"url_name": randomized_url_name, "class_name": long_name, "description": long_name}
        result = requests.post(url_root+"/classes/", data=class_obj)
        return_obj = {"status_code": result.status_code,
                      "data": result.json()}
        return return_obj

    def create_predefined_class(self, url_root):
        randomized_url_name = "test_predef_classs"
        long_name = "A Predefined Class for Testing"
        class_obj = {"url_name": randomized_url_name, "class_name": long_name, "description": long_name}
        result = requests.post(url_root+"/classes/", data=class_obj)
        return_obj = {"status_code": result.status_code,
                      "data": result.json()}
        return return_obj

    def list_keys_for_user(self, url_root, user):
        keys_result = requests.get(url_root+"/"+user+"/ssh_keys/")
        keys_obj = keys_result.json()
        return_obj = {"status_code": keys_result.status_code,
                      "data": keys_obj}
        return return_obj

    def add_randomized_key_to_user(self, url_root, user):
        ssh = SSHKeyLib()
        key = ssh.create_bogus_key()["pubkey_contents"]
        key_obj = {"pkey_contents": key}
        post_result = requests.post(url_root+"/"+user+"/ssh_keys/", data=key_obj)
        return_obj = {"status_code": post_result.status_code,
                      "data": post_result.json()}
        return return_obj

    def add_preset_key1_to_user(self, url_root, user):
        preset_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCqNP8fAI3WnE5zOjWPtJU3zSE7Dbm1x9qwY28DqXs+0s6UFjSc0WOGY5wsXUkzjgXK0U3TfAyiZOu7CAbQfWIpxTODjAu9UqRxMgGzWh/i/CO+uYrgb7hgVfXycyzrMHfKrA6vW7WjBQ2qfFz1GnVhXuvDMWlKROgTj/GvmGtVQz1olA9drvfcDE+z1+lT0moe4C/IFr7T3j6YROVEge6WvOD0Zxzj2awZ2SbLxdeup29AbOp4tbRC8qAK6cZWjkBRixyAiZ4yEsNr/CcM6Y/jpHuu6iCM59EtWFSEiujCcf1JRYaMbHVC4eqpwldwJy6c1lpfNULnS9aIQT8NNSGj shawkins@rrcs-97-77-50-220.sw.biz.rr.com"
        key_obj = {"pkey_contents": preset_key}
        post_result = requests.post(url_root+"/"+user+"/ssh_keys/", data=key_obj)
        return_obj = {"status_code": post_result.status_code,
                      "data": post_result.json()}
        return return_obj

    def add_preset_key2_to_user(self, url_root, user):
        preset_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDPISQ/uPxmzg1/bTbu16eyU+hGrR/MdJKNDgIh6X7OohSIfDyrfXgt3vz36VO6DaF94gV9Z+uRI+/JQsSfzg3r8LUt3JU9DFd5flxm01nknqYNyPF09uKXdcGr4SfmQ54hM0tq4/5NS0wkRRFbOplcvtDa3ZjXEmoFKAzXfxbknH+BkgBksjwL4L8m4o7ZxP21CHkAU8bfJDwjVdxtPhMiCQKqmsfj8P3ARTDj/e4CJmWrRaz9Xw4QMKDemkhzmJB/f0vjAmM3H7GzEsVsDTkNweHdDubp7Tynx5+QKv2iqZvgNJGA+ahcqJ/IUUtEPsAFFK5Hy6YOO4GT4nnZkOsD shawkins@rrcs-97-77-50-220.sw.biz.rr.com"
        key_obj = {"pkey_contents": preset_key}
        post_result = requests.post(url_root+"/"+user+"/ssh_keys/", data=key_obj)
        return_obj = {"status_code": post_result.status_code,
                      "data": post_result.json()}
        return return_obj

    def remove_key_from_user(self, root_url, user, key_to_remove):
        request_obj = {"pkey": key_to_remove}
        delete_result = requests.delete(root_url + "/" + user + "/ssh_keys/", data=request_obj)
        return_obj = {"status_code": delete_result.status_code,
                      "data": delete_result.json()}
        return return_obj