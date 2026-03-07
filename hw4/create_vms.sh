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
    --metadata-from-file=startup-script=listener-startup.sh

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
    --metadata-from-file=startup-script=server-startup.sh

WEBSERVER_IP=$(gcloud compute addresses describe hw4-webserver-ip \
  --region=$REGION --format='get(address)')
echo "Web Server IP: $WEBSERVER_IP"