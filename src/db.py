__author__ = 'Tsintsir'

from binascii import b2a_hex
from os import urandom
from pymongo import MongoClient
from pbkdf2 import PBKDF2


def create_user(username, email, password):
    client = MongoClient()
    db = client.gitsubmit.users
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
        raise LookupError("No such username could be found.")
    else:
        salt = user_doc["salt"]
        if b2a_hex(PBKDF2(password, salt).read(256)) == user_doc["hash"]:
            return True
        else:
            raise StandardError("Incorrect password.")