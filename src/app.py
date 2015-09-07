from flask.templating import render_template

__authors__ = ["shawkins", "Tsintsir", "sonph", "LeBat"]  # add yourself!

# internal (project libs)
from config import PORT_NUM
# base (python packages)
# external (pip packages)
from flask import Flask
import tornado.wsgi
import tornado.httpserver
import tornado.ioloop

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("hello.html")


@app.route('/my_var=<var>/')
def hello_var(var):
    return render_template("hello_var.html", var=var)

if __name__ == '__main__':
    wsgi_container = tornado.wsgi.WSGIContainer(app)
    http_server = tornado.httpserver.HTTPServer(wsgi_container)
    http_server.listen(PORT_NUM)
    tornado.ioloop.IOLoop.instance().start()
