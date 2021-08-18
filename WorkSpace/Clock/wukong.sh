#!/bin/bash


echo $1
cd $1
echo `pwd`
su pi -c "sudo python3 wukong.py"
