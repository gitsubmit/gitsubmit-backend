#!/usr/bin/env bash
killall python # in case any processes were left dangling
set -e # exit with non-zero exit codes immediately
if [ "$local_instance" = "yes" ]; then
    # this is on a server
    . ~/gitsubmitenv/bin/activate
else
    # This is probably being run locally by shawkins
    . /virtualenvs/gitsubmit_env/bin/activate
fi

python src/app.py -p 5123 &
sleep 3 # let tornado warm up
cd test

python -m robot.run --noncritical not_implemented .
killall python