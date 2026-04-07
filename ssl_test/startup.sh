#!/bin/bash
set -x 

exec > /var/log/startup-script.log 2>&1

apt-get update -y
apt-get install -y python3-pip git
git clone https://github.com/albhoe/528.git /opt/528
pip3 install --break-system-packages -r /opt/528/ssl_test/requirements.txt

gcloud config set project "bucsece528"

wait_for_metadata() {
  local status_code=0
  echo "Waiting for metadata server..."
  until [ "$status_code" -eq 200 ]; do
    status_code=$(curl -s -o /dev/null -w "%{http_code}" -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/id)
    sleep 2
  done
  echo "Metadata server is ready!"
}

wait_for_metadata

nohup python3 /opt/528/ssl_test/output.py > /var/log/server.log 2>&1 &