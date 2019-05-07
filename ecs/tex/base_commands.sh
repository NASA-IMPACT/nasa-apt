#!/bin/sh
apt-get update
apt-get install python3-pip --assume-yes
pip3 install --upgrade awscli
pip3 install -r requirements.txt