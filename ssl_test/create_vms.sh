#!/bin/bash

PROJECT_ID="bucsece528"
export REGION="us-east5"
export ZONE="${REGION}-c"
SERVICE_ACCOUNT="ssl_test_serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud config set project $PROJECT_ID

gcloud compute instances create testvm \
    --preemptible \
    --zone=$ZONE \
    --machine-type=e2-small \
    --service-account=$SERVICE_ACCOUNT \
    --scopes=cloud-platform \
    --tags=test-tag \
    --metadata="PROJECT_ID=${PROJECT_ID},REGION=${REGION},ZONE=${ZONE},SQL_INSTANCE=${SQL_INSTANCE},SERVICE_ACCOUNT=${SERVICE_ACCOUNT},SQL_INSTANCE=${SQL_INSTANCE},INSTANCE_CONNECTION_NAME=${INSTANCE_CONNECTION_NAME}"\
    --metadata-from-file=startup.sh \
    --project=$PROJECT_ID