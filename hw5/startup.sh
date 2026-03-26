#!/bin/bash
exec > /var/log/startup-script.log 2>&1
set -x

export PYTHONHTTPSVERIFY=0
export GOOGLE_CLOUD_PROJECT=bucsece528
gcloud auth application-default login --no-launch-browser
gcloud auth application-default print-access-token

apt-get update -y
apt-get install -y python3-pip python3-venv git

python3 -m venv /opt/venv
source /opt/venv/bin/activate

git clone https://github.com/albhoe/528.git /opt/528
pip install -r /opt/528/hw5/requirements.txt

nohup python3 /opt/528/hw5/hw5server.py > /root/server.log 2>&1 &