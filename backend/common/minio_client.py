import logging
from io import BytesIO

import pandas as pd
from minio import Minio


logger = logging.getLogger(__name__)

# This isn't not secure, just for sake of setup and prototype.
client = Minio("localhost:9000",
        secure=False,
        cert_check=False
)
dataframe_bucket_name = 'dataframes'


parquet_engine = 'pyarrow'
storage_file_extension = 'br'
compression = 'brotli'

def upload_dataframe(dataframe_id: str, version_id: str, df: pd.DataFrame):
    buffer = BytesIO()
    df.to_parquet(buffer, engine=parquet_engine, compression=compression)
    buffer.seek(0)

    destination_file = f"{dataframe_id}_{version_id}.{storage_file_extension}"
    found = client.bucket_exists(dataframe_bucket_name)
    if not found:
        client.make_bucket(dataframe_bucket_name)
        logger.info("Created bucket", dataframe_bucket_name)
    else:
        logger.info("Bucket ", dataframe_bucket_name, " already exists")

    client.put_object(
        dataframe_bucket_name,
        destination_file,
        buffer,
        -1,
        part_size=10*1024*1024
    )
    logger.info("DataFrame with id %s successfully uploaded as object", dataframe_id)

def get_dataframe(dataframe_id: str, version_id: str) -> pd.DataFrame:
    raw_byte = client.get_object(dataframe_bucket_name, f"{dataframe_id}_{version_id}.{storage_file_extension}")
    buffer = BytesIO()
    for d in raw_byte.stream(32*1024):
        buffer.write(d)
    buffer.seek(0)

    df = pd.read_parquet(buffer, engine=parquet_engine)
    return df
