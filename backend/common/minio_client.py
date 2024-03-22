from io import BytesIO

import pandas as pd
from minio import Minio


# This isn't not secure, just for sake of setup and demo.
client = Minio("localhost:9000",
        secure=False,
        cert_check=False
)

dataframe_bucket_name = 'dataframes'


def upload_dataframe(dataframe_id: str, version_id: str, df: pd.DataFrame):
    buffer = BytesIO()
    df.to_parquet(buffer, engine='pyarrow', compression='brotli')
    buffer.seek(0)

    destination_file = f"{dataframe_id}_{version_id}.br"
    found = client.bucket_exists(dataframe_bucket_name)
    if not found:
        client.make_bucket(dataframe_bucket_name)
        print("Created bucket", dataframe_bucket_name)
    else:
        print("Bucket", dataframe_bucket_name, "already exists")

    client.put_object(
        dataframe_bucket_name,
        destination_file,
        buffer,
        -1,  # Specify data size
        part_size=10*1024*1024
    )

    print(
        f"DataFrame with id {dataframe_id} successfully uploaded as object"
    )

def get_dataframe(dataframe_id: str, version_id: str) -> pd.DataFrame:
    raw_byte = client.get_object(dataframe_bucket_name, f"{dataframe_id}_{version_id}.br")
    buffer = BytesIO()
    for d in raw_byte.stream(32*1024):
        buffer.write(d)
    buffer.seek(0)

    df = pd.read_parquet(buffer, engine='pyarrow')
    return df
