from gitolite import GitoliteWrapper
from config import GITOLITE_ADMIN_PATH
from binascii import b2a_hex
from os import urandom
from pymongo import MongoClient
from pbkdf2 import PBKDF2
import subprocess



__author__ = ['Tsintsir', 'shawkins']

class UsernameAlreadyTakenError(Exception): pass
class EmailAlreadyTakenError(Exception): pass
class UrlNameAlreadyTakenError(Exception): pass
class ClassDoesNotExistError(Exception): pass
class ProjectDoesNotExistError(Exception): pass


def create_user(username, email, password):
    client = MongoClient()
    db = client.gitsubmit.users
    username_check_doc = db.find_one({"username": username})
    if username_check_doc is not None:
        raise UsernameAlreadyTakenError("That username is already taken.")
    email_check_doc = db.find_one({"email": email})
    if email_check_doc is not None:
        raise EmailAlreadyTakenError("That email address is already taken.")
    salt = urandom(256)
    db.insert_one(
        {
            "username": username,
            "email":    email,
            "salt":     salt,
            "hash":     b2a_hex(PBKDF2(password, salt).read(256))
        }
    )


def login(username, password):
    client = MongoClient()
    db = client.gitsubmit.users
    user_doc = db.find_one({"username": username})
    if user_doc is None:
        return False
    else:
        salt = user_doc["salt"]
        # TODO: return token
        if b2a_hex(PBKDF2(password, salt).read(256)) == user_doc["hash"]:
            return True
        else:
            return False


def create_class(url_name, long_name, owner):
    client = MongoClient()
    class_db = client.gitsubmit.classes

    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)
    # Make sure the owner exists
    gw.get_user_or_error(owner)

    # make sure urlname is unique
    shortname_check_doc = class_db.find_one({"url_name": url_name})
    if shortname_check_doc is not None:
        raise UrlNameAlreadyTakenError("That url name is already taken.")

    class_obj = {"url_name": url_name,
                 "long_name": long_name,
                 "owner": owner,
                 "teachers": [owner],
                 "students": []}

    return class_db.insert_one(class_obj)


def create_project(url_name, long_name, parent_class_url_name, is_team_based, due_date, owner, max_team_size=4):
    """
    :param url_name: The raw project url name. Do not include the parent class or /'es!
    """
    # form the git clone url (see functional requirements)
    gitolite_url = parent_class_url_name + "/" + url_name

    client = MongoClient()
    project_db = client.gitsubmit.projects
    class_db = client.gitsubmit.classes

    # Make sure the url_name is unique
    shortname_check_doc = project_db.find_one({"gitolite_url": gitolite_url})
    if shortname_check_doc is not None:
        raise UrlNameAlreadyTakenError("That url name is already taken for that class.")

    # Ensure the parent class exists
    parent_class_obj = class_db.find_one({"url_name": parent_class_url_name})
    if parent_class_obj is None:
        raise ClassDoesNotExistError(str(parent_class_url_name))

    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)
    # Make sure the owner exists
    gw.get_user_or_error(owner)

    # Add the teachers of the parent class to the project with RW permissions
    repo = gw.create_repo(gitolite_url, owner)
    for teacher in parent_class_obj["teachers"]:
        gw.give_user_readwrite_permission(teacher, repo.name)

    # If we've gotten here without exception, add to the DB
    project_obj = {"gitolite_url": gitolite_url,
                   "url_name": url_name,
                   "long_name": long_name,
                   "parent": parent_class_url_name,
                   "is_team_based": is_team_based,
                   "owner": owner,
                   "due": due_date,
                   "max_team_size": max_team_size}

    return project_db.insert_one(project_obj)


def create_submission(url_name, long_name, parent_project_url, owner):
    """
    :param url_name: The urlname given by the user. Do not include /'es or username!
    """
    # Form the git clone url (see functional requirements)
    submission_full_git_url = owner + "/submissions/" + url_name

    client = MongoClient()
    submission_db = client.gitsubmit.submissions
    project_db = client.gitsubmit.projects
    class_db = client.gitsubmit.classes

    # Make sure the url_name is unique
    shortname_check_doc = submission_db.find_one({"gitolite_url": submission_full_git_url})
    if shortname_check_doc is not None:
        raise UrlNameAlreadyTakenError("That url name is already taken.")

    # Ensure the parent project exists
    parent_project_obj = project_db.find_one({"url_name": parent_project_url})
    if parent_project_obj is None:
        raise ProjectDoesNotExistError(str(parent_project_url))
    parent_class_obj = class_db.find_one({"url_name": parent_project_obj["parent"]})
    if parent_class_obj is None:
        raise ClassDoesNotExistError(str(parent_project_obj["parent"]))
    parent_class_url = parent_class_obj


    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)
    # Make sure the owner exists
    gw.get_user_or_error(owner)

    # Note: create_repo sets the repo ACCESS rights in gitolite
    gw.create_repo(submission_full_git_url, owner)

    # This is what actually causes the fork, though
    parent_project_full_git_url = parent_class_url + "/" + parent_project_url
    fork_callstring = "ssh git@localhost fork " + parent_project_full_git_url + " " + submission_full_git_url
    subprocess.call(fork_callstring, shell=True)

    # If we got here, nothing went wrong, stuff it in the db
    submission_obj = {"gitolite_url": submission_full_git_url,
                      "long_name": long_name,
                      "owner": owner,
                      "parent": parent_project_url,
                      "contributors": [owner]}

    return submission_db.insert_one(submission_obj)
