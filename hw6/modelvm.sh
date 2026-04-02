#!/bin/bash

exec > /var/log/startup-script.log 2>&1
set -ex

if [ -f /var/log/startup_already_done ]; then
   exit 0
fi

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
sudo dpkg -i mysql*.deb
sudo apt-get -f install

pip3 install --break-system-packages pymysql
pip3 install --break-system-packages sqlalchemy
pip3 install --break-system-packages "cloud-sql-python-connector[pymysql]"


gcloud config set project "bucsece528"

#Load files through GitHub
git clone https://github.com/albhoe/528.git /opt/528
pip3 install --break-system-packages -r /opt/528/hw6/requirements.txt

touch /var/log/startup_already_done

PROJECT_ID="${PROJECT_ID:-bucsece528}"
REGION="${REGION:-us-east5}"
ZONE="${ZONE:-${REGION}-a}"
SQL_INSTANCE="${SQL_INSTANCE:-alhoe-hw5-mysqlinstance}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-hw4-client-serviceaccount@${PROJECT_ID}.iam.gserviceaccount.com}"
INSTANCE_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${SQL_INSTANCE}"
 
export PROJECT_ID REGION ZONE SQL_INSTANCE SERVICE_ACCOUNT INSTANCE_CONNECTION_NAME
 
nohup python3 -u /opt/528/hw6/model.py > /var/log/server.log 2>&1 &