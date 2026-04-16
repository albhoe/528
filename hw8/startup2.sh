#!/bin/bash
set -x 
exec > /var/log/startup-script.log 2>&1

apt-get update -y
apt-get install -y python3-pip python3-venv git ca-certificates
update-ca-certificates
apt-get install -y ntpdate
ntpdate -u pool.ntp.org

ZONE2="us-south1-b"
PROJECT_ID="bucsece528"

cleanup() {
   echo "Exit Called. Cleaning up resources..."
   gcloud compute instances suspend testvm2 --zone=$ZONE2 --quiet
}

trap cleanup EXIT

git clone https://github.com/albhoe/528.git /opt/528

# Create a virtual environment
python3 -m venv /opt/venv
source /opt/venv/bin/activate

# Install requirements inside the venv
pip install -r /opt/528/hw8/requirements.txt

pip install requests

export GCE_METADATA_MTLS_MODE=none

# Run the script using the venv python
nohup /opt/venv/bin/python3 /opt/528/hw8/client.py > /var/log/client.log 2>&1 &