from flask import *
from google.cloud import storage
from google.cloud import pubsub_v1
import logging
import google.cloud.logging
import pymysql
import time

PROJECT_ID = "bucsece528"

client = google.cloud.logging.Client(project=PROJECT_ID)
client.setup_logging(project=PROJECT_ID)

app = Flask(__name__)

BANNED_COUNTRIES = ['North Korea', 'Iran', 'Cuba', 'Myanmar', 'Iraq', 'Libya', 'Sudan', 'Zimbabwe', 'Syria']

storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket('alhoe528hw2')
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("bucsece528", "hw3topic")

def connect_to_db():
    return pymysql.connect(
        host='35.226.17.220',
        user='root',
        password='',
        database='cs528-hw5-database'
    )

def headers(request):
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

def send_requestdata(data):
    connection = connect_to_db()
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO requests
              (timestamp,country, client_ip, gender, age, income, is_banned, time_of_day, requested_file)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, tuple(data.values()))
    connection.commit()

def send_faildata(data,error_code):
    log_entry = tuple(data['timestamp'],data['time_of_day'],data['path'],error_code)
    connection = connect_to_db()
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO errors
              (timestamp, time_of_day, requested_file, error_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, log_entry)
    connection.commit()

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'])
def process_request(request):
    if request.method == "GET":
        headers = headers(request)
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
            send_faildata(headers,400)
            return 'Permission Denied', 400

        name = request.args.get('file')
        blob = bucket.blob(name)
        if blob.exists():
            send_requestdata(headers)
            return blob.download_as_text(), 200
        else:
            logging.error({"message": "File not found", "file": name})
            send_faildata(headers,404)
            return f"Not Found Error: {name} does not exist", 404
    else:
        logging.error({'message':'Request for unimplemented function','method':request.method})
        send_faildata(headers,501)
        return "Not Implemented", 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)