#!/bin/bash
exec > /var/log/startup-script.log 2>&1
set -x

if [ -f /var/log/startup_already_done ]; then
   exit 0
fi

apt-get update -y
pip3 install -y python3-pip git

#Connect to database programmatically
wget https://dev.mysql.com/get/Downloads/MySQL-8.4/mysql-server_8.4.8-1ubuntu20.04_amd64.deb-bundle.tar
tar -xvf mysql-server_8.4.8-1ubuntu20.04_amd64.deb-bundle.tar
sudo apt-get install libaio1
sudo dpkg-preconfigure mysql-community-server_*.deb
sudo dpkg -i mysql*.deb
sudo apt-get -f install

pip3 install pymysql
pip3 install sqlalchemy
pip3 install "cloud-sql-python-connector[pymysql]"

export PROJECT_ID=bucsece528
export DB_USER=root
export DB_PASS=''
export DB_NAME=cs528-hw5-database
export INSTANCE_CONNECTION_NAME= bucsece528\:us-east1\:alhoe-hw5-mysqlinstance

#Load files through GitHub
git clone https://github.com/albhoe/528.git /opt/528
pip3 install -r /opt/528/hw5/requirements.txt

touch /var/log/startup_already_done

nohup python3 /opt/528/hw5/hw5server.py > /root/server.log 2>&1 &