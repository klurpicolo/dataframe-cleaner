import logging
import os
from io import BytesIO

import pandas as pd
from minio import Minio


MINIO_URL = os.getenv("MINIO_URL")


logger = logging.getLogger(__name__)

# This isn't not secure, just for sake of setup and prototype.
client = Minio(MINIO_URL, secure=False, cert_check=False)
dataframe_bucket_name = "dataframes"


PARQUET_ENGINE = "pyarrow"
STORAGE_FILE_EXTENSION = "br"
COMPRESSION = "brotli"


def upload_dataframe(dataframe_id: str, version_id: str, df: pd.DataFrame):
    buffer = BytesIO()
    df.to_parquet(buffer, engine=PARQUET_ENGINE, compression=COMPRESSION)
    buffer.seek(0)

    destination_file = f"{dataframe_id}_{version_id}.{STORAGE_FILE_EXTENSION}"
    found = client.bucket_exists(dataframe_bucket_name)
    if not found:
        client.make_bucket(dataframe_bucket_name)
        logger.info("Created bucket", dataframe_bucket_name)
    else:
        logger.info("Bucket ", dataframe_bucket_name, " already exists")

    client.put_object(
        dataframe_bucket_name, destination_file, buffer, -1, part_size=10 * 1024 * 1024
    )
    logger.info("DataFrame with id %s successfully uploaded as object", dataframe_id)


def get_dataframe(dataframe_id: str, version_id: str) -> pd.DataFrame:
    raw_byte = client.get_object(
        dataframe_bucket_name, f"{dataframe_id}_{version_id}.{STORAGE_FILE_EXTENSION}"
    )
    buffer = BytesIO()
    for d in raw_byte.stream(32 * 1024):
        buffer.write(d)
    buffer.seek(0)

    df = pd.read_parquet(buffer, engine=PARQUET_ENGINE)
    return df
