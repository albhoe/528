#!/bin/bash

set -x

PROJECT_ID="bucsece528"
export REGION="us-south1"
export ZONE1="${REGION}-a"
SERVICE_ACCOUNT="ssl-test-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud config set project $PROJECT_ID

gcloud compute instances delete testvm1 --zone=$ZONE1 --quiet || true

gcloud compute instances create testvm1 \
    --zone=$ZONE1 \
    --machine-type=e2-small \
    --service-account=$SERVICE_ACCOUNT \
    --scopes=cloud-platform \
    --tags=hw4-webserver \
    --metadata-from-file=startup-script=startup2.sh \
    --project=$PROJECT_ID
