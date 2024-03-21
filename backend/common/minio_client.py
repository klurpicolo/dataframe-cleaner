from io import BytesIO

import pandas as pd
from minio import Minio


client = Minio("localhost:9000",
        secure=False,
        cert_check=False
)

dataframe_bucket_name = 'dataframes'

# TODO use the proper encrypt data type
def upload_dataframe(dataframe_id: str, version_id: str, df: pd.DataFrame):
    raw_byte = BytesIO(df.to_csv(index=False).encode('utf-8'))
    destination_file = f"{dataframe_id}_{version_id}"
    found = client.bucket_exists(dataframe_bucket_name)
    if not found:
        client.make_bucket(dataframe_bucket_name)
        print("Created bucket", dataframe_bucket_name)
    else:
        print("Bucket", dataframe_bucket_name, "already exists")

    client.put_object(
        dataframe_bucket_name,
        destination_file,
        raw_byte,
        -1,  # Specify data size
        part_size=10*1024*1024
    )

    print(
        f"DataFrame with id {dataframe_id} successfully uploaded as object"
    )

def get_dataframe(dataframe_id: str, version_id: str) -> pd.DataFrame:
    raw_byte = client.get_object(dataframe_bucket_name, f"{dataframe_id}_{version_id}")

    buffer = BytesIO()
    for d in raw_byte.stream(32*1024):
        buffer.write(d)
    buffer.seek(0)

    df = pd.read_csv(buffer)

    return df
