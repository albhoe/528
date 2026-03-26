#!/bin/bash
exec > /var/log/startup-script.log 2>&1
set -x

if [ -f /var/log/startup_already_done ]; then
   exit 0
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y python3-pip python3-venv git ca-certificates

# Create and activate venv
python3 -m venv /opt/venv
source /opt/venv/bin/activate

# Upgrade pip and install certifi
pip3 install --upgrade pip
pip3 install certifi

# Tell Python where the certificates are
export SSL_CERT_FILE=$(python3 -m certifi)
export REQUESTS_CA_BUNDLE=$(python3 -m certifi)

git clone https://github.com/albhoe/528.git /opt/528
pip3 install -r /opt/528/hw5/requirements.txt

sudo apt-get update && sudo apt-get install google-guest-agent
sudo apt-get update && sudo apt-get install --reinstall ca-certificates
sudo update-ca-certificates

touch /var/log/startup_already_done [cite: 50]

nohup python3 /opt/528/hw5/hw5server.py > /root/server.log 2>&1 &