#!/bin/bash

set -x

PROJECT_ID="bucsece528"
export REGION="us-south1"
export ZONE="${REGION}-a"
SERVICE_ACCOUNT="ssl-test-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud config set project $PROJECT_ID

gcloud compute instances delete testvm --zone=$ZONE --quiet || true

gcloud compute instances create testvm \
    --zone=$ZONE \
    --machine-type=e2-small \
    --service-account=$SERVICE_ACCOUNT \
    --scopes=cloud-platform \
    --tags=test-tag \
    --metadata-from-file=startup-script=startup.sh \
    --project=$PROJECT_ID