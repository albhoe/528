from flask import *
from google.cloud import storage
from google.cloud import pubsub_v1
import logging

app = Flask(__name__)

storage_client = storage.Client()
bucket = storage_client.bucket('alhoe528hw2')
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("bucsece528", "hw3topic")

@app.route("/")
def process_request(request):
    if request.method == "GET":
        country = request.headers.get('X-country')
        if country in ['North Korea', 'Iran', 'Cuba', 'Myanmar', 'Iraq', 'Libya', 'Sudan', 'Zimbabwe', 'Syria']:
            message = f'Permission Denied because X-country header = {country}'
            logging.error({'message':message})
            data = message.encode("utf-8")
            publisher.publish(topic_path, data)
            return 'Permission Denied', 400

        name = request.args.get('file')
        blob = bucket.blob(name)
        if blob.exists():
            return blob.download_as_text(), 200
        else:
            logging.error({"message": "File not found", "file": name})
            return f"Not Found Error: {name} does not exist", 404
    else:
        logging.error({'message':'Request for unimplemented function','method':request.method})
        return "Not Implemented", 501