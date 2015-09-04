__author__ = 'shawkins'

import os

"""
Various project configurations
"""
LOCAL_INSTANCE = "local_instance" in os.environ.keys() and os.environ["local_instance"] == "yes"
PORT_NUM = 8080 if LOCAL_INSTANCE else 80
