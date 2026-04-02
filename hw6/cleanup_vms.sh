ZONE=${ZONE:-us-east5-a}

gcloud compute instances delete hw6vm --zone=$ZONE --quiet