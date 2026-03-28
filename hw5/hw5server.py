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
from google.cloud.exceptions import NotFound

_storage_client = None
_bucket = None



from google.colab import auth

auth.authenticate_user()
     

PROJECT_ID = os.getenv('PROJECT_ID', 'bucsece528')
INSTANCE_CONNECTION_NAME = os.getenv('INSTANCE_CONNECTION_NAME', 'bucsece528:us-east5:alhoe-hw5-mysqlinstance-b')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', '')
DB_NAME = os.getenv('DB_NAME', 'cs528-hw5-database')

logging_client = google.cloud.logging.Client(project=PROJECT_ID)
logging_client.setup_logging()

app = Flask(__name__)

BANNED_COUNTRIES = ['North Korea', 'Iran', 'Cuba', 'Myanmar', 'Iraq', 'Libya', 'Sudan', 'Zimbabwe', 'Syria']


def get_bucket():
    global _storage_client, _bucket
    if _bucket is None:
        _storage_client = storage.Client(project=PROJECT_ID)
        _bucket = _storage_client.bucket('alhoe528hw2')
    return _bucket

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("bucsece528", "hw3topic")

connector = Connector()

def getconn():
    conn = connector.connect(
      INSTANCE_CONNECTION_NAME,
      "pymysql",
      user=DB_USER,
      password=DB_PASS,
      db=DB_NAME
    )
    print(f"Database connection established successfully: {conn}")
    return conn

pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)
print(f"Database connection pool created: {pool}")

def get_headers(request):
    start = time.perf_counter()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') #USE THIS AS PRIMARY KEY
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
        age = int(request.headers.get('X-age', -1))
    except:
        age = -1

    try:
        income = float(request.headers.get('X-income', -1))
    except:
        income = -1

    try:
        path = request.args.get('file')
    except: 
        path = ''
    elapsed = time.perf_counter() - start
    logging.info(f"[TIMING] Header extraction: {elapsed:.6f}s")
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

def send_requestdata(data, db_conn):
    print(f"Logging request data: {data}")
    start = time.perf_counter()
    db_conn.execute(sqlalchemy.text("""
        INSERT INTO requests
        (timestamp, country, client_ip, gender, age, income, is_banned, time_of_day, requested_file)
        VALUES (:timestamp, :country, :client_ip, :gender, :age, :income, :is_banned, :time_of_day, :requested_file)
    """), {
        'timestamp':      data['timestamp'],
        'country':        data['country'],
        'client_ip':      data['client_ip'],
        'gender':         data['gender'],
        'age':            data['age'],
        'income':         data['income'],
        'is_banned':      data['is_banned'],
        'time_of_day':    data['time_of_day'],
        'requested_file': data['requested_file']
    })
    db_conn.commit()
    elapsed = time.perf_counter() - start
    logging.info(f"[TIMING] Database insert: {elapsed:.6f}s")
    
def send_faildata(data, error_code, db_conn):
    print(f"Logging error with code {error_code} for request: {data}")
    db_conn.execute(sqlalchemy.text("""
        INSERT INTO errors
        (timestamp, time_of_day, requested_file, error_code)
        VALUES (:timestamp, :time_of_day, :requested_file, :error_code)
    """), {
        'timestamp':      data['timestamp'],
        'time_of_day':    data['time_of_day'],
        'requested_file': data['requested_file'],
        'error_code':     error_code
    })
    db_conn.commit()

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'])
def process_request():
    print(f"Received {request.method} request at / endpoint")
    with pool.connect() as db_conn:
        print(f"Database connection acquired from pool: {db_conn}")
        headers = get_headers(request)
        print(f"Extracted headers: {headers}")
        if request.method == "GET":
            print("Processing GET request")
            country = request.headers.get('X-country') #I could extract the header using the function, but I'm scared of breaking things.
            if country in BANNED_COUNTRIES:
                print(f"Country {country} is banned. Logging and returning 403.")
                message = f'Permission Denied because X-country header = {country}'
                data = message.encode("utf-8")
                try:
                    future = publisher.publish(topic_path, data)
                    future.result(timeout=10)
                    print("Published message to Pub/Sub successfully")
                except Exception as e:
                    logging.error(f'Publish Error:{e}')
                logging.error({'message':message})
                send_faildata(headers,400,db_conn)
                print("Inserted error data into database")
                return 'Permission Denied', 400
            print(f"Country {country} is not banned. Proceeding to check for requested file.")
            name = request.args.get('file')
            print(f"Requested file: {name}")
            if name:
                print("file parameter is not null")
                blob = get_bucket().blob(name)
                print(f"Blob: {blob}")
                try:
                    start = time.perf_counter()
                    content = blob.download_as_text()
                    elapsed = time.perf_counter() - start
                    logging.info(f"[TIMING] File read from GCS: {elapsed:.6f}s")
                    print(f"File {name} found in bucket. Logging request data and returning content.")
                    send_requestdata(headers,db_conn)
                    print("Inserted request data into database")
                    return content, 200
                except NotFound:
                    print(f"File {name} not found in bucket. Logging error and returning 404.")
                    logging.error({"message": "File not found", "file": name})
                    send_faildata(headers,404,db_conn)
                    return f"Not Found Error: {name} does not exist", 404
                except Exception as e:
                    elapsed = time.perf_counter() - start
                    print(f"Error downloading file {name} after {elapsed:.6f}s: {e}")
                    logging.error(f"Error downloading file {name} after {elapsed:.6f}s: {e}")
                    return f"Error downloading file {name}", 500
            
            print("file parameter is null. Logging error and returning 404.")
            logging.error({"message": "File not found", "file": name})
            send_faildata(headers,404,db_conn)
            print("Inserted error data into database for file not found")
            return f"Not Found Error: {name} does not exist", 404
        else:
            logging.error({'message':'Request for unimplemented function','method':request.method})
            send_faildata(headers,501,db_conn)
            print("Inserted error data into database for unimplemented method")
            return "Not Implemented", 501

if __name__ == "__main__":
    print("Starting Flask application")
    app.run(host="0.0.0.0", port=8080, threaded=True)