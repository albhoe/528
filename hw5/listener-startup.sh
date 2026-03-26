#!/bin/bash
exec > /var/log/startup-script.log 2>&1
set -x

apt-get update -y
sudo apt-get install --reinstall ca-certificates
apt-get install -y python3-pip git
git clone https://github.com/albhoe/528.git /opt/528
pip3 install --break-system-packages -r /opt/528/hw5/requirements.txt
nohup python3 /opt/528/hw5/listener.py > /root/listener.log 2>&1 &