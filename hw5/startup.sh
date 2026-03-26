#!/bin/bash
exec > /var/log/startup-script.log 2>&1
set -x

if [ -f /var/log/startup_already_done ]; then
   exit 0
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y python3-pip python3-venv git

# Create and activate venv
python3 -m venv /opt/venv
source /opt/venv/bin/activate

pip3 install --upgrade pip

git clone https://github.com/albhoe/528.git /opt/528
pip3 install -r /opt/528/hw5/requirements.txt

touch /var/log/startup_already_done

nohup python3 /opt/528/hw5/hw5server.py > /root/server.log 2>&1 &