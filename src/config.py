import os
import argparse

__author__ = 'shawkins'

"""
Various project configurations
"""
LOCAL_INSTANCE = "local_instance" in os.environ.keys() and os.environ["local_instance"] == "yes"
PORT_NUM = 8080 if LOCAL_INSTANCE else 80

# Method of sending in configs via command-line args
arg_parser = argparse.ArgumentParser(description='Optional app.py arguments')
arg_parser.add_argument("--port_num", "-p", required=False)