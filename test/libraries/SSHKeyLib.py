import os
import binascii
import subprocess

__author__ = 'shawkins'


class SSHKeyLib(object):
    def create_bogus_key(self):
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
