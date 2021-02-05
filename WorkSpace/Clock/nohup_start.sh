#!/bin/bash

BASEDIR=`dirname $0`
echo "work on $BASEDIR"
cd $BASEDIR


sudo nohup ./main.py >> nohup.log 2>&1 &


