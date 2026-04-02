exec > /var/log/startup-script.log 2>&1
set -x

if [ -f /var/log/startup_already_done ]; then
   exit 0
fi

apt-get update -y
apt-get install -y python3-pip git wget

#Connect to database programmatically
wget https://dev.mysql.com/get/Downloads/MySQL-8.4/mysql-server_8.4.8-1debian13_amd64.deb-bundle.tar
tar -xvf mysql-server_8.4.8-1debian13_amd64.deb-bundle.tar
sudo apt-get install libaio1
sudo dpkg-preconfigure mysql-community-server_*.deb
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

nohup env PROJECT_ID=$PROJECT_ID,\  
    REGION=$REGION,\
    ZONE=$ZONE,\
    SQL_INSTANCE=$SQL_INSTANCE,\
    SERVICE_ACCOUNT=$SERVICE_ACCOUNT,\
    SQL_INSTANCE=$SQL_INSTANCE,\
    INSTANCE_CONNECTION_NAME=$PROJECT_ID:$REGION:$SQL_INSTANCE"\
    python3 -u /opt/528/hw6/model.py > /var/log/server.log 2>&1 &