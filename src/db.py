__author__ = 'Tsintsir'

from bson import Binary
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
            "hash":     Binary.new(PBKDF2(password, salt).read(256))    # TODO: This doesn't store successfully; expects a string
        }
    )