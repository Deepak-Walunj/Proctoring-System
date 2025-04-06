from google.cloud import storage
from google.oauth2 import service_account
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the relative path
credentials_path = os.path.join(current_dir, "gen-lang-client-0166846330-97747717adf2.json")

# Set the environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path


credentials = service_account.Credentials.from_service_account_file(credentials_path)

    # Create a storage client with the credentials
storage_clients = storage.Client(credentials=credentials, project="gen-lang-client-0166846330")

bucket_name='eduviva'



# source_file_name="C:/Development/Web-Dev/Project-1/Semester_project/backend/mlmodel/audio_gtJyDGw.wav"
destination_blob_name="file1"
def upload_blob(source_file_name, destination_blob_name):
    print("uploading on gcs")
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage_clients
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )
    uri=f"gs://eduviva/{destination_blob_name}"
    return uri


# print(upload_blob(source_file_name=source_file_name,destination_blob_name=destination_blob_name))