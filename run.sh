#!/bin/bash

source ./venv/bin/activate

pip install -r requeriment.txt

eval $(python decript.py fdata.kdb)


hypercorn --bind 127.0.0.1:5000 HiveCash.hiveCash:app -w 1 >> logs/weblog.txt 2>&1 & 

export webpid=`echo $!`
echo "$webpid" > pids/web.pid
echo "Web  start at pid $webpid"


