#!/bin/bash

exec > /var/log/startup-script.log 2>&1
set -ex

if [ -f /var/log/startup_already_done ]; then
   exit 0
fi


ZONE="${ZONE:-${REGION:-us-east5}-a}"

cleanup() {
   echo "Exit Called. Cleaning up resources..."
   gcloud compute instances suspend hw6vm --zone=$ZONE --quiet
   #gcloud sql instances patch $SQL_INSTANCE --activation-policy=NEVER --quiet --project=$PROJECT_ID
}

trap cleanup EXIT

echo 'Acquire::ForceIPv4 "true";' | tee /etc/apt/apt.conf.d/99force-ipv4
dpkg --configure -a
apt --fix-broken install -y
apt-get clean

sudo apt-get update
sudo apt-get install -y \
   python3-distutils \
   python3-setuptools \
   python3-wheel \
   python3-dev \
   build-essential \
   git \
   wget

wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
python3 /tmp/get-pip.py --break-system-packages
rm /tmp/get-pip.py

python3 --version
pip3 --version
git --version

#Connect to database programmatically
wget https://dev.mysql.com/get/Downloads/MySQL-8.4/mysql-server_8.4.8-1debian13_amd64.deb-bundle.tar
tar -xvf mysql-server_8.4.8-1debian13_amd64.deb-bundle.tar
sudo apt-get install libaio1
#sudo dpkg-preconfigure mysql-community-server_*.deb
#sudo dpkg -i mysql*.deb
#sudo apt-get -f install

pip3 install --break-system-packages pymysql
pip3 install --break-system-packages sqlalchemy
pip3 install --break-system-packages "cloud-sql-python-connector[pymysql]"

gcloud config set project "bucsece528"
gcloud config set auth/disable_ssl_validation True

#sudo apt-get update && sudo apt-get --only-upgrade install google-cloud-cli-cloud-run-proxy google-cloud-cli-minikube google-cloud-cli-enterprise-certificate-proxy google-cloud-cli-kubectl-oidc google-cloud-cli-app-engine-python google-cloud-cli-sbom-extractor google-cloud-cli-istioctl google-cloud-cli google-cloud-cli-cbt google-cloud-cli-app-engine-go google-cloud-cli-gke-gcloud-auth-plugin google-cloud-cli-config-connector google-cloud-cli-anthoscli google-cloud-cli-docker-credential-gcr google-cloud-cli-log-streaming google-cloud-cli-nomos kubectl google-cloud-cli-package-go-module google-cloud-cli-spanner-migration-tool google-cloud-cli-anthos-auth google-cloud-cli-datastore-emulator google-cloud-cli-pubsub-emulator google-cloud-cli-cloud-build-local google-cloud-cli-local-extract google-cloud-cli-bigtable-emulator google-cloud-cli-skaffold google-cloud-cli-managed-flink-client google-cloud-cli-app-engine-python-extras google-cloud-cli-app-engine-java google-cloud-cli-spanner-cli google-cloud-cli-spanner-emulator google-cloud-cli-run-compose google-cloud-cli-terraform-tools google-cloud-cli-firestore-emulator google-cloud-cli-app-engine-grpc google-cloud-cli-kpt

#apt install python3-certifi

set VERIFY_SSL_CERTS=false
set COLLECT_ANALYTICS=False
set SENTRY_DSN=''
set FRONTEND_SENTRY_DSN=label-studio start
export GRPC_DEFAULT_SSL_ROOTS_FILE_PATH=/etc/ssl/certs/ca-certificates.crt

#Load files through GitHub
git clone https://github.com/albhoe/528.git /opt/528
pip3 install --break-system-packages -r /opt/528/hw6/requirements.txt


#sudo apt-get install -y ca-certificates
#sudo update-ca-certificates

touch /var/log/startup_already_done

PROJECT_ID="${PROJECT_ID:-bucsece528}"
REGION="${REGION:-us-east5}"
SQL_INSTANCE="${SQL_INSTANCE:-alhoe-hw5-mysqlinstance}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-hw4-client-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com}"
INSTANCE_CONNECTION_NAME="${PROJECT_ID}:us-central1:${SQL_INSTANCE}"
 
export PROJECT_ID REGION ZONE SQL_INSTANCE SERVICE_ACCOUNT INSTANCE_CONNECTION_NAME
 
python3 -u /opt/528/hw6/model.py > /var/log/server.log 2>&1

gcloud compute instances suspend hw6vm --zone=$ZONE --quiet

echo "Full Run successful. Suspending the VM to save costs..."