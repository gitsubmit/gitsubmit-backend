#!/usr/bin/env bash
killall python # in case any processes were left dangling
set -e # exit with non-zero exit codes immediately
if [ -z "$local_instance" ]; then
    # this is on a server
    . ~/gitsubmitenv/bin/activate
else
    # This is probably being run locally by shawkins
    . /virtualenv/gitsubmit_env/bin/activate
fi

cd ..
python src/app.py -p 5123 &
sleep 3 # let tornado warm up
cd test

python -m robot.run --noncritical not_implemented .
killall python