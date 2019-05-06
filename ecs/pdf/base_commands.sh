#!/bin/sh
apt-get update
apt-get install python3-pip --assume-yes
pip3 install --upgrade awscli

apt-get install -y texlive-latex-recommended

apt-get --assume-yes install wget