#!/bin/bash

set -e 

PROJECT_ID="bucsece528"
BUCKET="alhoe528hw2"
REGION="us-central1"
ZONE="us-central1-a"
WEBSERVER_SERVICE_ACCOUNT="hw4-webserver-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"
FORBIDDEN_SERVICE_ACCOUNT="hw4-forbidden-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud config set project $PROJECT_ID

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
    --address=webserver-ip \
    --metadata-from-file=startup-script=startup.sh

gcloud compute instances create hw4-forbidden \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --service-account=$FORBIDDEN_SERVICE_ACCOUNT \
    --scopes=cloud-platform \
    --tags=hw4-forbidden \
    --metadata-from-file=startup-script=listener-startup.sh