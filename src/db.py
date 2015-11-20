from datetime import datetime, timedelta
import os
import shutil
from gitolite import GitoliteWrapper
from config import TIME_FORMAT, STATIC_REPOS_ROOT
from binascii import b2a_hex
from os import urandom
from pymongo import MongoClient
from pbkdf2 import PBKDF2
import subprocess
import jwt

__author__ = ['Tsintsir', 'shawkins']

class UsernameAlreadyTakenError(Exception): pass
class EmailAlreadyTakenError(Exception): pass
class UrlNameAlreadyTakenError(Exception): pass
class ClassDoesNotExistError(Exception): pass
class ProjectDoesNotExistError(Exception): pass
class SubmissionDoesNotExistError(Exception): pass


class DatabaseWrapper(object):

    def __init__(self, gitolite_admin_path, port=None, ssh_host="localhost", repositories_root=STATIC_REPOS_ROOT):
        self.mongo = MongoClient(port=port)
        self.ssh_host = ssh_host
        self.glpath = gitolite_admin_path
        self.repo_root = repositories_root

    def create_user(self, username, email, password, first_name, last_name):
        db = self.mongo.gitsubmit.users
        username_check_doc = db.find_one({"username": username})
        if username_check_doc is not None:
            raise UsernameAlreadyTakenError("That username is already taken.")
        email_check_doc = db.find_one({"email": email})
        if email_check_doc is not None:
            raise EmailAlreadyTakenError("That email address is already taken.")
        salt = urandom(256).encode('base64')
        db.insert_one(
            {
                "username": username,
                "email":    email,
                "first_name": first_name,
                "last_name": last_name,
                "salt":     salt,
                "hash":     b2a_hex(PBKDF2(password, salt).read(256))
            }
        )

    def login(self, username, password):
        db = self.mongo.gitsubmit.users
        user_doc = db.find_one({"username": username})
        if user_doc is None:
            return False
        else:
            salt = user_doc["salt"]
            # TODO: Better secret handling
            if b2a_hex(PBKDF2(password, salt).read(256)) == user_doc["hash"]:
                return jwt.encode({'username': username, 'exp': datetime.utcnow() + timedelta(hours=2)}, 'gitsubmitsecret')
            else:
                return False

    def update_email(self, username, new_email):
        db = self.mongo.gitsubmit.users
        user_doc = db.find_one({"username": username})
        if user_doc is not None:
            user_doc["email"] = new_email
            db.update({"_id": user_doc["_id"]}, user_doc)

    def update_password(self, username, new_password):
        db = self.mongo.gitsubmit.users
        user_doc = db.find_one({"username": username})
        if user_doc is not None:
            salt = user_doc["salt"]
            user_doc["hash"] = b2a_hex(PBKDF2(new_password, salt).read(256))
            db.update({"_id": user_doc["_id"]}, user_doc)

    def get_all_classes(self):
        class_db = self.mongo.gitsubmit.classes
        classes = [cl for cl in class_db.find(projection={"_id": False})]
        return classes

    def get_class_or_error(self, class_url):
        class_db = self.mongo.gitsubmit.classes
        class_obj = class_db.find_one({"url_name": class_url}, projection={"_id": False})
        if class_obj is None:
            raise ClassDoesNotExistError(str(class_url))
        return class_obj

    def add_student_to_class(self, class_url, username):
        class_obj = self.get_class_or_error(class_url)
        # student = get_student_or_error() # TODO: this
        class_obj["students"].append(username)
        class_db = self.mongo.gitsubmit.classes
        class_db.update({"url_name": class_url}, class_obj)
        return class_obj

    def add_teacher_to_class(self, class_url, username):
        class_obj = self.get_class_or_error(class_url)
        # teacher = get_teacher_or_error() # TODO: this
        class_obj["teachers"].append(username)
        class_db = self.mongo.gitsubmit.classes
        class_db.update({"url_name": class_url}, class_obj)
        return class_obj

    def get_overdue_projects_for_class(self, class_url):
        project_db = self.mongo.gitsubmit.projects
        projects = [self.fix_dates_in_project_obj(p) for p in project_db.find({"parent": class_url}, projection={"_id": False}) if p["due"] <= datetime.now()]
        return projects

    def get_ontime_projects_for_class(self, class_url):
        project_db = self.mongo.gitsubmit.projects
        projects = [self.fix_dates_in_project_obj(p) for p in project_db.find({"parent": class_url}, projection={"_id": False}) if p["due"] > datetime.now()]
        return projects

    def get_all_projects_for_class(self, class_url):
        project_db = self.mongo.gitsubmit.projects
        projects = [self.fix_dates_in_project_obj(p) for p in project_db.find({"parent": class_url}, projection={"_id": False})]
        return projects

    def get_project_or_error(self, class_url, project_url):
        project_db = self.mongo.gitsubmit.projects
        project_obj = project_db.find_one({"url_name": project_url, "parent": class_url}, projection={"_id": False})
        if project_obj is None:
            raise ProjectDoesNotExistError(str(project_obj))
        return self.fix_dates_in_project_obj(project_obj)

    def create_class(self, url_name, long_name, description, owner):
        class_db = self.mongo.gitsubmit.classes

        gw = GitoliteWrapper(self.glpath)
        # Make sure the owner exists
        gw.get_user_or_error(owner)

        # make sure urlname is unique
        shortname_check_doc = class_db.find_one({"url_name": url_name})
        if shortname_check_doc is not None:
            raise UrlNameAlreadyTakenError("That url name is already taken.")

        class_obj = {"url_name": url_name,
                     "long_name": long_name,
                     "description": description,
                     "owner": owner,
                     "teachers": [owner],
                     "students": []}

        return class_db.insert_one(class_obj)

    def create_project(self, url_name, long_name, description, parent_class_url_name, is_team_based, due_date, owner, max_team_size=4):
        """
        :param url_name: The raw project url name. Do not include the parent class or /'es!
        """
        # apply defaults in case None
        if max_team_size is None:
            max_team_size = 4

        # form the git clone url (see functional requirements)
        gitolite_url = parent_class_url_name + "/" + url_name

        project_db = self.mongo.gitsubmit.projects
        class_db = self.mongo.gitsubmit.classes

        # Make sure the url_name is unique
        shortname_check_doc = project_db.find_one({"gitolite_url": gitolite_url})
        if shortname_check_doc is not None:
            raise UrlNameAlreadyTakenError("That url name is already taken for that class.")

        # Ensure the parent class exists
        parent_class_obj = class_db.find_one({"url_name": parent_class_url_name})
        if parent_class_obj is None:
            raise ClassDoesNotExistError(str(parent_class_url_name))

        gw = GitoliteWrapper(self.glpath)
        # Make sure the owner exists
        gw.get_user_or_error(owner)

        # Add the teachers of the parent class to the project with RW permissions
        repo = gw.create_repo(gitolite_url, owner)
        for teacher in parent_class_obj["teachers"]:
            gw.give_user_readwrite_permission(teacher, repo.name)

        due_datetime = datetime.strptime(due_date, TIME_FORMAT)

        # If we've gotten here without exception, add to the DB
        project_obj = {"gitolite_url": gitolite_url,
                       "url_name": url_name,
                       "long_name": long_name,
                       "description": description,
                       "parent": parent_class_url_name,
                       "is_team_based": is_team_based,
                       "owner": owner,
                       "due": due_datetime,
                       "max_team_size": max_team_size}

        return project_db.insert_one(project_obj)

    def update_project_due_date(self, class_url, project_url, new_date_str):
        _unused_class_obj = self.get_class_or_error(class_url)
        project_obj = self.get_project_or_error(class_url, project_url)

        due_datetime = datetime.strptime(new_date_str, TIME_FORMAT)

        project_obj["due"] = due_datetime

        project_db = self.mongo.gitsubmit.projects
        project_db.update({"url_name": project_url}, project_obj)
        return self.fix_dates_in_project_obj(project_obj)

    def create_submission(self, url_name, long_name, parent_project_url, owner):
        """
        :param url_name: The urlname given by the user. Do not include /'es or username!
        """
        # Form the git clone url (see functional requirements)
        submission_full_git_url = owner + "/submissions/" + url_name

        submission_db = self.mongo.gitsubmit.submissions
        project_db = self.mongo.gitsubmit.projects
        class_db = self.mongo.gitsubmit.classes

        # Make sure the url_name is unique
        shortname_check_doc = submission_db.find_one({"gitolite_url": submission_full_git_url})
        if shortname_check_doc is not None:
            raise UrlNameAlreadyTakenError("That url name is already taken.")

        # Ensure the parent project exists
        parent_project_obj = project_db.find_one({"gitolite_url": parent_project_url})
        if parent_project_obj is None:
            raise ProjectDoesNotExistError(str(parent_project_url))
        parent_class_obj = class_db.find_one({"url_name": parent_project_obj["parent"]})
        if parent_class_obj is None:
            raise ClassDoesNotExistError(str(parent_project_obj["parent"]))
        parent_class_url = parent_class_obj["url_name"]

        gw = GitoliteWrapper(self.glpath)
        # Make sure the owner exists
        gw.get_user_or_error(owner)

        # This is what actually causes the fork
        fork_callstring = "ssh git@" + self.ssh_host + " fork " + parent_project_url + " " + submission_full_git_url
        subprocess.call(fork_callstring, shell=True)

        # now create_repo sets the repo ACCESS rights in gitolite
        gw.create_repo(submission_full_git_url, owner)

        # If we got here, nothing went wrong, stuff it in the db
        submission_obj = {"gitolite_url": submission_full_git_url,
                          "long_name": long_name,
                          "owner": owner,
                          "parent": parent_project_url,
                          "contributors": [owner]}

        result = submission_db.insert_one(submission_obj)

        dest_dir = os.path.abspath(os.path.join(self.repo_root, submission_full_git_url+".git"))

        exists = os.path.exists(dest_dir)

        dest_file = os.path.join(dest_dir, "hooks", "pre-receive")
        src_hook = os.path.abspath(os.path.join("src", "hooks", "pre-receive"))

        print "src", src_hook
        print "dest", dest_file
        print "exists", exists

        shutil.copy(src_hook, dest_file)

        return result

    def delete_submission(self, gitolite_url):
        submission_db = self.mongo.gitsubmit.submissions
        cursor = submission_db.find({"gitolite_url": gitolite_url})

        if cursor.count() < 1:
            raise SubmissionDoesNotExistError(gitolite_url)

        for item in cursor:
            submission_db.remove(item["_id"])

    def fix_dates_in_project_obj(self, project_obj):
        if "due" in project_obj.keys() and type(project_obj["due"]) is datetime:
            project_obj["due"] = project_obj["due"].strftime(TIME_FORMAT)
        return project_obj

    def get_submission_or_error(self, gitolite_url):
        submission_db = self.mongo.gitsubmit.submissions
        submission_obj = submission_db.find_one({"gitolite_url": gitolite_url}, projection={"_id": False})
        if submission_obj is None:
            raise SubmissionDoesNotExistError(str(gitolite_url))
        return submission_obj

    # TODO: implement this function. Modify submission object and repo
    # Raised errors should be handled in the API as well, so don't forget!
    def add_contributor(self, username, submission_name, new_contributor):
        return False

    # TODO: implement this function. Modify submission object and repo privileges
    # Raised errors should be handled in the API as well, so don't forget!
    def remove_contributor(self, username, submission_name, removed_contributor):
        return False

    def get_contributors(self, username, submission_name):
        submission_db = self.mongo.gitsubmit.submissions
        submission_doc = submission_db.find_one({"owner": username, "long_name": submission_name})
        if submission_doc is None:
            raise SubmissionDoesNotExistError(str(username) + ": " + str(submission_name))
        return submission_doc["contributors"]

    def get_projects_for_user(self, username):
        project_db = self.mongo.gitsubmit.projects
        result_cursor = project_db.find({"owner": username}, projection={"_id": False})
        projects = [p for p in result_cursor]
        projects = [self.fix_dates_in_project_obj(p) for p in projects]
        return projects

    def get_submissions_for_user(self, username):
        submission_db = self.mongo.gitsubmit.submissions
        result_cursor = submission_db.find( { "$or": [ {"owner": username}, {"contributors": username} ] }, projection={"_id": False})
        submissions = [s for s in result_cursor]
        return submissions

    def get_classes_for_user(self, username):
        class_db = self.mongo.gitsubmit.classes
        result_cursor = class_db.find( { "$or": [ {"owner": username}, {"teachers": username}, {"students": username} ] }, projection={"_id": False})
        classes = [c for c in result_cursor]
        return classes

    def is_past_deadline(self, submission_gitolite_url):
        """ returns bool, datetime  (e.g. True, <datetime object> ) """
        submission = self.get_submission_or_error(submission_gitolite_url)
        project_db = self.mongo.gitsubmit.projects

        parent_project_url = submission["parent"]

        parent_project_obj = project_db.find_one({"gitolite_url": parent_project_url})
        if parent_project_obj is None:
            raise ProjectDoesNotExistError(str(parent_project_url))

        deadline = parent_project_obj["due"]
        now = datetime.now()

        result = now > deadline
        return result, deadline
