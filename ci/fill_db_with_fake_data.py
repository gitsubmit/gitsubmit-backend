import hashlib
from os import urandom
import datetime
import os
import binascii
from pymongo import MongoClient
from pbkdf2 import PBKDF2
from binascii import b2a_hex
import subprocess
import sys
sys.path.append("src")
from gitolite import GitoliteWrapper

__author__ = 'shawkins'
import argparse


def create_bogus_key():
    random_name = "bogus_key_" + binascii.b2a_hex(os.urandom(15))[:8]  # generate a random 8-char name
    callstring = "ssh-keygen -b 2048 -t rsa -f "+ random_name +" -q -N \"\""
    subprocess.call("pwd")
    subprocess.call(callstring, shell=True)
    with open(os.path.abspath(random_name + ".pub")) as pkey:
        pubkey_contents = pkey.read()
    bogus_key = {"private_path": os.path.abspath(random_name),
                 "pub_path": os.path.abspath(random_name + ".pub"),
                 "pubkey_contents": pubkey_contents}
    return bogus_key

def convert_ssh_key_to_colon_string(key):
    hexstring = hashlib.md5(key.strip().split()[1]).hexdigest()
    colonstring = ':'.join(hexstring[i:i+2] for i in range(0, len(hexstring), 2))
    return colonstring

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--mongo_port", help="the mongodb port to connect to", type=int)
    parser.add_argument( "-pyo", "--pyolite_location", help="the folder pyolite should bind to")
    args = parser.parse_args()

    mongoclient = MongoClient(port=args.mongo_port)

    gitsubmit_db = mongoclient.get_database("gitsubmit")
    user_collection = gitsubmit_db.get_collection("users")

    salt = urandom(256)
    password = "verybadpw"

    # make some students
    student1 = {
        "username": "student1",
        "email": "student1@gmail.com",
        "salt": salt,
        "hash": b2a_hex(PBKDF2(password, salt).read(256))
    }

    student2 = {
        "username": "student2",
        "email": "student2@gmail.com",
        "salt": salt,
        "hash": b2a_hex(PBKDF2(password, salt).read(256))
    }

    # make some teachers
    teacher1 = {
        "username": "teacher1",
        "email": "teacher1@gmail.com",
        "salt": salt,
        "hash": b2a_hex(PBKDF2(password, salt).read(256))
    }

    teacher2 = {
        "username": "teacher2",
        "email": "teacher2@gmail.com",
        "salt": salt,
        "hash": b2a_hex(PBKDF2(password, salt).read(256))
    }

    user_collection.insert_one(student1)
    user_collection.insert_one(student2)
    user_collection.insert_one(teacher1)
    user_collection.insert_one(teacher2)

    class_collection = gitsubmit_db.get_collection("classes")

    intro_to_computers = {"url_name": "intro_to_computers",
                          "long_name": "Introduction to Computers",
                          "description": "Introduction to Computers description",
                          "owner": "teacher1",
                          "teachers": ["teacher1"],
                          "students": ["student1"]}
    advanced_computers = {"url_name": "adv_computers",
                          "long_name": "Advanced Computers",
                          "description": "Advanced Computers description",
                          "owner": "teacher2",
                          "teachers": ["teacher2"],
                          "students": ["student2"]}

    class_collection.insert_one(intro_to_computers)
    class_collection.insert_one(advanced_computers)

    project_collection = gitsubmit_db.get_collection("projects")

    turn_on_a_computer = {"gitolite_url": "intro_to_computers/turn_on_a_computer",
                          "url_name": "turn_on_a_computer",
                          "long_name": "Turn on a computer",
                          "description": "ToaC description",
                          "parent": "intro_to_computers",
                          "is_team_based": False,
                          "owner": "teacher1",
                          "due": datetime.datetime.now() + datetime.timedelta(days=5),
                          "max_team_size": 4}

    use_a_computer = {"gitolite_url": "adv_computers/use_a_computer",
                          "url_name": "use_a_computer",
                          "long_name": "Use a computer",
                          "description": "UaC description",
                          "parent": "adv_computers",
                          "is_team_based": True,
                          "owner": "teacher2",
                          "due": datetime.datetime.now() + datetime.timedelta(days=3),
                          "max_team_size": 4}

    project_collection.insert_one(turn_on_a_computer)
    project_collection.insert_one(use_a_computer)

    submission_db = gitsubmit_db.get_collection("submissions")

    turned_on_computer = {"gitolite_url": "student1/submissions/turned_on_computer",
                    "long_name": "Student 1 turned on a computer",
                    "owner": "student1",
                    "parent": "intro_to_computers",
                    "contributors": ["student1"]}

    used_a_computer = {"gitolite_url": "student2/submissions/used_a_computer",
                    "long_name": "Student 2 used a computer",
                    "owner": "student2",
                    "parent": "adv_computers",
                    "contributors": ["student2", "student1"]}

    submission_db.insert_one(turned_on_computer)
    submission_db.insert_one(used_a_computer)

    gw = GitoliteWrapper(args.pyolite_location)
    bogus_key = create_bogus_key()
    gw.add_pkey_to_user("student1", bogus_key)
