#!/bin/bash

set -e 

PROJECT_ID="bucsece528"
BUCKET="alhoe528hw2"
REGION="us-central1"
ZONE="us-central1-a"
WEBSERVER_SERVICE_ACCOUNT="hw4-webserver-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"
FORBIDDEN_SERVICE_ACCOUNT="hw4-forbidden-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"

# Allocate the static IP
gcloud compute addresses create webserver-ip \
    --region=$REGION \
    --project=$PROJECT_ID

# Retrieve the allocated IP into a variable
STATIC_IP=$(gcloud compute addresses describe webserver-ip \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format='get(address)')

echo "Static IP allocated: $STATIC_IP"

#Create Web Server 
gcloud compute instances create hw4-webserver \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --service-account=$WEBSERVER_SERVICE_ACCOUNT \
    --scopes=cloud-platform \
    --tags=hw4-webserver \
    --address=hw4-webserver-ip \
    --address=$STATIC_IP \
    --metadata-from-file startup-script=startup.sh \

WEBSERVER_IP=$(gcloud compute addresses describe hw4-webserver-ip \
  --region=$REGION --format='get(address)')
echo "Web Server IP: $WEBSERVER_IP (Check that this matches the static IP allocated above)"