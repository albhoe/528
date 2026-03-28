#!/bin/bash
set -e

PROJECT_ID="bucsece528"
BUCKET="alhoe528hw2"
REGION="us-east5"
ZONE="us-east5-a"
WEBSERVER_SERVICE_ACCOUNT="hw4-webserver-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"
FORBIDDEN_SERVICE_ACCOUNT="hw4-forbidden-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"
SQL_INSTANCE="alhoe-hw5-mysqlinstance-b"

gcloud config set project $PROJECT_ID

PROJECT_ID=bucsece528
DB_USER=root
DB_PASS=''
DB_NAME=cs528-hw5-database
INSTANCE_CONNECTION_NAME=bucsece528:us-east5:alhoe-hw5-mysqlinstance-b

# ── Static IP ─────────────────────────────────────────────────────────────────
gcloud compute addresses create webserver-ip \
    --region=$REGION \
    --project=$PROJECT_ID

STATIC_IP=$(gcloud compute addresses describe webserver-ip \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format='get(address)')

echo "Static IP allocated: $STATIC_IP"

#Adds this IP to the authorized networks of the SQL instance so that the webserver can connect to it
#I think this resets every time the IP changes, so it doesn't strictly need to be in the cleanup script.

# ── Cloud SQL ──────────────────────────────────────────────────────────────────
DB_EXISTS=$(gcloud sql databases list \
    --instance=$SQL_INSTANCE \
    --project=$PROJECT_ID \
    --filter="name=cs528-hw5-database" \
    --format="value(name)" 2>/dev/null || echo "")

if [ -z "$DB_EXISTS" ]; then
    echo "Starting Cloud SQL instance and creating schema..."
    gcloud sql instances patch $SQL_INSTANCE \
        --activation-policy=ALWAYS \
        --authorized-networks=$STATIC_IP \
        --quiet \
        --project=$PROJECT_ID
    # Wait for it to be ready
    gcloud sql operations wait \
        $(gcloud sql operations list \
            --instance=$SQL_INSTANCE \
            --project=$PROJECT_ID \
            --format="value(name)" \
            --limit=1) \
        --project=$PROJECT_ID
    python3 startup_schema.py
else
    echo "Database exists, just starting Cloud SQL instance..."
    gcloud sql instances patch $SQL_INSTANCE \
        --activation-policy=ALWAYS \
        --authorized-networks=$STATIC_IP \
        --quiet \
        --project=$PROJECT_ID
fi

# ── VMs ───────────────────────────────────────────────────────────────────────
gcloud compute instances create hw4-webserver \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --service-account=$WEBSERVER_SERVICE_ACCOUNT \
    --scopes=cloud-platform \
    --tags=hw4-webserver \
    --address=webserver-ip \
    --metadata-from-file=startup-script=startup.sh \
    --project=$PROJECT_ID

gcloud compute instances create hw4-forbidden \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --service-account=$FORBIDDEN_SERVICE_ACCOUNT \
    --scopes=cloud-platform \
    --tags=hw4-forbidden \
    --metadata-from-file=startup-script=listener-startup.sh \
    --project=$PROJECT_ID