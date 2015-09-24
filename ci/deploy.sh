#!/usr/bin/env bash
killall python || true # and ignore if it wasn't already running
set -e
. /virtualenvs/gitsubmit_env/bin/activate # turn on the gitsubmit virtual python environment
cd /srv/gitsubmit
git pull origin master
git submodule init
git submodule update
git submodule status
pip install -r requirements.txt # get python packages
cd src
nohup /virtualenvs/gitsubmit_env/bin/gunicorn --access-logfile /srv/logs/access.log -w 10 -b :80 app:app &
# -w = number workers, -b = socket to bind (blank ip = broadcast, 0.0.0.0, port = 80)
sleep 3
curl http://gitsubmit.com/