import boto3
import os
from botocore.exceptions import NoCredentialsError
from app.config import settings

# Create a local directory for scans fallback if needed
LOCAL_UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static_uploads"))
os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)

async def upload_to_s3(file_bytes: bytes, s3_key: str) -> str:
    """
    Uploads binary bytes to AWS S3. 
    If AWS credentials are not configured, falls back to saving files locally 
    and returning a local web server URL.
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        # Verify AWS credentials
        import io
        s3_client.upload_fileobj(
            io.BytesIO(file_bytes),
            settings.S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={'ACL': 'public-read'}
        )
        
        return f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
    except (NoCredentialsError, Exception) as e:
        print(f"[!] S3 Upload Failed (or bypassed): {e}. Saving to local server cache.")
        
        # Local fallback execution
        local_path = os.path.join(LOCAL_UPLOAD_DIR, s3_key.replace("/", "_"))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        with open(local_path, "wb") as f:
            f.write(file_bytes)
            
        # Return local server URL path
        return f"http://localhost:8000/static/{s3_key.replace('/', '_')}"
