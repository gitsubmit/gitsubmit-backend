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
cd /srv/logs
nohup python /srv/gitsubmit/src/app.py &
sleep 3
curl http://gitsubmit.com/