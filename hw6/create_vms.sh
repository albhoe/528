#!/bin/bash

PROJECT_ID="bucsece528"
REGION='us-east5'
ZONE=$REGION-a
SQL_INSTANCE="alhoe-hw5-mysqlinstance"

SERVICE_ACCOUNT=hw4-client-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com
SQL_INSTANCE="alhoe-hw5-mysqlinstance"
INSTANCE_CONNECTION_NAME=$PROJECT_ID:$REGION:$SQL_INSTANCE

gcloud config set project $PROJECT_ID

gcloud compute instances create hw6vm \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --service-account=$SERVICE_ACCOUNT \
    --scopes=cloud-platform \
    --tags=hw4-webserver \
    --address=webserver-ip \
    --metadata=PROJECT_ID="$PROJECT_ID,\
        REGION=$REGION,\
        ZONE=$ZONE,\
        SQL_INSTANCE=$SQL_INSTANCE,\
        SERVICE_ACCOUNT=$SERVICE_ACCOUNT,\
        SQL_INSTANCE=$SQL_INSTANCE,\
        INSTANCE_CONNECTION_NAME=$PROJECT_ID:$REGION:$SQL_INSTANCE"\
    --metadata-from-file=startup-script=modelvm.sh \
    --project=$PROJECT_ID