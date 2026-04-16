#!/bin/bash

set -x

PROJECT_ID="bucsece528"
export REGION="us-south1"
export ZONE1="${REGION}-a"
export ZONE2="${REGION}-b"
SERVICE_ACCOUNT="ssl-test-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud config set project $PROJECT_ID

gcloud compute instance-groups unmanaged remove-instances hw8-ig1 \
    --instances=testvm1 --zone=$ZONE1 --quiet || true

gcloud compute instance-groups unmanaged remove-instances hw8-ig2 \
    --instances=testvm2 --zone=$ZONE2 --quiet || true

gcloud compute instances delete testvm1 --zone=$ZONE1 --quiet || true
gcloud compute instances delete testvm2 --zone=$ZONE2 --quiet || true

gcloud compute instances create testvm1 \
    --zone=$ZONE1 \
    --machine-type=e2-small \
    --service-account=$SERVICE_ACCOUNT \
    --scopes=cloud-platform \
    --tags=hw4-webserver \
    --metadata-from-file=startup-script=startup1.sh \
    --project=$PROJECT_ID

gcloud compute instances create testvm2 \
    --zone=$ZONE2 \
    --machine-type=e2-small \
    --service-account=$SERVICE_ACCOUNT \
    --scopes=cloud-platform \
    --tags=hw4-webserver \
    --metadata-from-file=startup-script=startup1.sh \
    --project=$PROJECT_ID

gcloud compute instance-groups unmanaged add-instances hw8-ig1 \
    --instances=testvm1 --zone=$ZONE1 --quiet || true
gcloud compute instance-groups unmanaged add-instances hw8-ig2 \
    --instances=testvm2 --zone=$ZONE2 --quiet || true