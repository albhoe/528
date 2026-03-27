#!/bin/bash

PROJECT_ID="bucsece528"
REGION='us-east5'
ZONE='us-east5-a'
SQL_INSTANCE="alhoe-hw5-mysqlinstance"

# Stop Cloud SQL (do NOT delete it)
gcloud sql instances patch $SQL_INSTANCE \
    #--activation-policy=NEVER \
    --clear-authorized-networks \
    --project=$PROJECT_ID


# Delete VMs
gcloud compute instances delete hw4-forbidden --zone=$ZONE --quiet
gcloud compute instances delete hw4-webserver --zone=$ZONE --quiet

# Release static IP
gcloud compute addresses delete webserver-ip \
    --region=$REGION \
    --quiet