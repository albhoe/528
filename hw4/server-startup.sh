#!/bin/bash
exec > /var/log/startup-script.log 2>&1
set -x

apt-get update -y
apt-get install -y python3-pip git
git clone https://github.com/albhoe/528.git /opt/528
pip3 install --break-system-packages -r /opt/528/hw4/requirements.txt
export BUCKET_NAME='alhoe528hw2'
export PORT=8080
nohup python3 /opt/528/hw4/server.py > /root/server.log 2>&1 &