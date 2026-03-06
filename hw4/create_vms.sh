#!/bin/bash

set -e 

PROJECT_ID="bucsece528"
BUCKET="alhoe528hw2"
REGION="us-central1"
ZONE="us-central1-a"
WEBSERVER_SERVICE_ACCOUNT="hw4-webserver-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"
FORBIDDEN_SERVICE_ACCOUNT="hw4-forbidden-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud compute instances create hw4-forbidden \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --service-account=$FORBIDDEN_SERVICE_ACCOUNT \
    --scopes=cloud-platform \
    --metadata=startup-script='#!/bin/bash
    apt-get update -y && pip3 install --break-system-packages requests
    
    git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git /opt/hw4

nohup python3 /opt/hw4/listener.py > /var/log/listener.log 2>&1 &'