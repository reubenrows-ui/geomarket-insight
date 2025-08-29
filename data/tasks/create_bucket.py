from google.cloud import storage

def ensure_bucket(bucket_name: str, location: str = "US"):
    """
    Ensure a GCS bucket exists. If it doesn't, create it.

    Args:
        bucket_name: name of the GCS bucket
        location: region (e.g., "US", "us-central1")
    """
    client = storage.Client()

    try:
        bucket = client.get_bucket(bucket_name)
        print(f"✅ Bucket already exists: {bucket.name}")
        return bucket
    except Exception:
        # Not found → create
        bucket = client.bucket(bucket_name)
        bucket.location = location
        bucket = client.create_bucket(bucket)
        print(f"✅ Created bucket: {bucket.name} [{bucket.location}]")
        return bucket
