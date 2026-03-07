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
    --tags=hw4-forbidden \
    --metadata=startup-script='#!/bin/bash
    sudo apt-get update -y 
    sudo apt-get install -y python3-pip git
    sudo git clone https://github.com/albhoe/528.git /opt
    sudo pip3 install --break-system-packages -r /opt/hw4/requirements.txt 
    sudo nohup python3 /opt/hw4/listener.py > /var/log/listener.log 2>&1 &'

sleep 10
REPORTER_IP=$(gcloud compute instances describe hw4-forbidden \
    --zone=$ZONE \
    --format='get(networkInterfaces[0].networkIP)')
echo "Forbidden VM IP: $REPORTER_IP" 

#Create Web Server 
gcloud compute instances create hw4-webserver \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --service-account=$WEBSERVER_SERVICE_ACCOUNT \
    --scopes=cloud-platform \
    --tags=hw4-webserver \
    --address=hw4-webserver-ip \
    --metadata=startup-script='#!/bin/bash
    sudo apt-get update -y
    sudo apt-get install -y python3-pip git
    sudo git clone https://github.com/albhoe/528.git /opt
    sudo pip3 install --break-system-packages -r /opt/hw4/requirements.txt
    export BUCKET_NAME='alhoe528hw2'
    export PORT=8080
    
    sudo nohup python3 /opt/hw4/server.py > /var/log/server.log 2>&1 &'

WEBSERVER_IP=$(gcloud compute addresses describe hw4-webserver-ip \
  --region=$REGION --format='get(address)')
echo "Web Server IP: $WEBSERVER_IP"