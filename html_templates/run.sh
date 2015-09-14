#!/bin/bash
git pull && git submodule init && git submodule update && git submodule status
if which python 2>&1 > /dev/null; then
    python -m SimpleHTTPServer
else
    echo 'Python is not installed'
fi
