from google.cloud import storage

project_id="bucsece528"
bucket_name="alhoe528hw2"
blob_name="server_test"


client = storage.Client(project=project_id)
bucket = client.bucket('alhoe528hw2')
blob = bucket.blob(blob_name)
blob.upload_from_string('Hello, world! (Server)')
print("Done. (Server)")

from flask import *
from google.cloud import storage
from google.cloud import pubsub_v1
import logging
import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
import requests

zone_url = "http://metadata.google.internal/computeMetadata/v1/instance/zone"
headers = {"Metadata-Flavor": "Google"}

try:
    response = requests.get(zone_url, headers=headers, timeout=5)
    response.raise_for_status()
    full_zone = response.text
    print(full_zone)
    print(full_zone.split('/')[-1])
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

app = Flask(__name__)

storage_client = storage.Client()
bucket = storage_client.bucket('alhoe528hw2')
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("bucsece528", "hw3topic")

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'])
def handle_request():
    if request.method == "GET":
        country = request.headers.get('X-country')
        if country in ['North Korea', 'Iran', 'Cuba', 'Myanmar', 'Iraq', 'Libya', 'Sudan', 'Zimbabwe', 'Syria']:
            message = f'Permission Denied because X-country header = {country}'
            logging.critical(message)
            data = message.encode("utf-8")
            try:
                future = publisher.publish(topic_path, data)
                future.result(timeout=10)
            except Exception as e:
                logging.error(f'Publish Error:{e}')
            return 'Permission Denied', 400

        name = request.args.get('file')
        blob = bucket.blob(name)
        if blob.exists():
            return blob.download_as_text(), 200
        else:
            logging.warning(f"File not found:{name}")
            return f"Not Found Error: {name} does not exist", 404
    else:
        logging.warning(f"Request for unimplemented function: {request.method}")
        return "Not Implemented", 501
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)