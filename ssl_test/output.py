from google.cloud import storage

project_id="bucsece528"
bucket_name="alhoe528hw2"
blob_name="test"


client = storage.Client(project='bucsece528')
bucket = client.bucket('alhoe528hw2')
blob = bucket.blob(blob_name)
blob.upload_from_string('Hello, world!')