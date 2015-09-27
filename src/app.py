from flask.templating import render_template

__authors__ = ["shawkins", "Tsintsir", "sonph", "LeBat"]  # add yourself!

# internal (project libs)
from config import PORT_NUM, arg_parser

# base (python packages)
import sys

# external (pip packages)
from flask import Flask
import tornado.wsgi
import tornado.httpserver
import tornado.ioloop

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/my_var=<var>/')
def hello_var(var):
    return render_template("hello_var.html", var=var)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

