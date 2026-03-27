from flask import Flask, request
from google.cloud import storage
from google.cloud import pubsub_v1
import logging
import google.cloud.logging
import time
import os
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import socket, struct
import sqlalchemy

PROJECT_ID = os.getenv('PROJECT_ID', 'bucsece528')
INSTANCE_CONNECTION_NAME = os.getenv('INSTANCE_CONNECTION_NAME', '')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', '')
DB_NAME = os.getenv('DB_NAME', 'cs528-hw5-database')

_logging_client = None

def get_logging_client():
    global _logging_client
    if _logging_client is None:
        _logging_client = google.cloud.logging.Client(project=PROJECT_ID)
        _logging_client.setup_logging()
    return _logging_client

app = Flask(__name__)

BANNED_COUNTRIES = ['North Korea', 'Iran', 'Cuba', 'Myanmar', 'Iraq', 'Libya', 'Sudan', 'Zimbabwe', 'Syria']

storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket('alhoe528hw2')
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("bucsece528", "hw3topic")

connector = Connector()

def getconn():
    conn = connector.connect(
      INSTANCE_CONNECTION_NAME,
      "pymysql",
      user=DB_USER,
      password=DB_PASS,
      db=DB_NAME,
      ip_type=IPTypes.PRIVATE
    )
    return conn

pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

def get_headers(request):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S'), #USE THIS AS PRIMARY KEY
    tod = time.strftime('%H:%M:%S')
    client_ip = request.remote_addr

    try:
        country = request.headers.get('X-country')
    except:
        country = ''

    try:
        gender = request.headers.get('X-gender')
    except:
        gender = ''

    try:
        age = int(request.headers.get('X-age', 0))
    except:
        age = -1

    try:
        income = float(request.headers.get('X-income', 0))
    except:
        income = -1

    try:
        path = request.args.get('file')
    except: 
        path = ''

    return {
        'timestamp':      timestamp,
        'country':        country,
        'client_ip':      client_ip,
        'gender':         gender,
        'age':            age,
        'income':         income,
        'is_banned':      country in BANNED_COUNTRIES,
        'time_of_day':    tod,
        'requested_file': path
    }

def send_requestdata(data,connection):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO requests
              (timestamp,country, client_ip, gender, age, income, is_banned, time_of_day, requested_file)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, tuple(data.values()))
    connection.commit()

def send_faildata(data,error_code,connection):
    log_entry = (data['timestamp'],data['time_of_day'],data['requested_file'],error_code)
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO errors
              (timestamp, time_of_day, requested_file, error_code)
            VALUES (%s, %s, %s, %s)
        """, log_entry)
    connection.commit()

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'])
def process_request():
    connection=connect_to_db()
    get_logging_client()
    if request.method == "GET":
        headers = get_headers(request)
        country = request.headers.get('X-country') #I could extract the header using the function, but I'm scared of breaking things.
        if country in BANNED_COUNTRIES:
            message = f'Permission Denied because X-country header = {country}'
            data = message.encode("utf-8")
            try:
                future = publisher.publish(topic_path, data)
                future.result(timeout=10)
            except Exception as e:
                logging.error(f'Publish Error:{e}')
            logging.error({'message':message})
            send_faildata(headers,400,connection)
            return 'Permission Denied', 400

        name = request.args.get('file')
        if name:
            blob = bucket.blob(name)
            if blob.exists():
                send_requestdata(headers,connection)
                return blob.download_as_text(), 200
        
        logging.error({"message": "File not found", "file": name})
        send_faildata(headers,404,connection)
        return f"Not Found Error: {name} does not exist", 404
    else:
        logging.error({'message':'Request for unimplemented function','method':request.method})
        send_faildata(headers,501,connection)
        return "Not Implemented", 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)