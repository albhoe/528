from google.cloud import pubsub_v1
from google.cloud import storage

storage_client = storage.Client()
bucket = storage_client.bucket('alhoe528hw2')
blob = bucket.blob('/hw3/forbidden_countries_log.txt')

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path("bucsece528", "hw3subscription")

def callback(message):
    try:
        print(f"Received forbidden request alert: {message.data.decode('utf-8')}")
        if blob.exists():
            logs = blob.download_as_text()
        else:
            logs = ""
        logs += message.data.decode('utf-8') + "\n"
        blob.upload_from_string(logs)
        message.ack()
    except Exception as e:
        print(f"Error processing message: {e}")
        message.nack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}...")

try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()