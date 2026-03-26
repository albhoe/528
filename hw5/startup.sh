#!/bin/bash
exec > /var/log/startup-script.log 2>&1
set -x

apt-get update -y
apt-get install -y python3-pip git

pip3 install --break-system-packages google-auth==2.22.0
pip3 install --break-system-packages requests==2.28.2

export GOOGLE_METADATA_SERVICE_HTTPS=false
echo "export GOOGLE_METADATA_SERVICE_HTTPS=false" >> /etc/environment

git clone https://github.com/albhoe/528.git /opt/528
pip3 install --break-system-packages -r /opt/528/hw5/requirements.txt
export BUCKET_NAME='alhoe528hw2'
export PORT=8080
nohup python3 /opt/528/hw5/hw5server.py > /root/server.log 2>&1 &