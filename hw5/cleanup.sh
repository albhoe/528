#!/bin/bash

PROJECT_ID="bucsece528"
REGION='us-east5'
ZONE='us-east5-a'

gcloud compute instances delete hw4-forbidden --zone=$ZONE --quiet
gcloud compute instances delete hw4-webserver --zone=$ZONE --quiet

# Then release the static IP
gcloud compute addresses delete webserver-ip \
    --region=$REGION \
    --quiet