#!/bin/bash

PROJECT_ID="bucsece528"
REGION='us-central1'
ZONE='us-central1-a'

gcloud compute instances delete hw4-forbidden --zone=$ZONE --quiet
gcloud compute instances delete hw4-webserver --zone=$ZONE --quiet