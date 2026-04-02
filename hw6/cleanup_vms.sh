ZONE=${ZONE:-us-central1-a}

gcloud compute instances delete hw6vm --zone=$ZONE --quiet