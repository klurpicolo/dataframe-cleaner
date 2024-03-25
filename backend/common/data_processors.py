import logging
import math
import time
from multiprocessing import Pool

import pandas as pd

from .minio_client import upload_dataframe
from .mongo_client import update_status
from .processing_enum import OperationType, ProcessStatus


logger = logging.getLogger(__name__)


def infer_col(col: pd.Series) -> pd.Series:
    start_time = time.time()
    infer_type = pd.api.types.infer_dtype(col, skipna=True)
    logger.info("infer type from pandas col %s is %d", col.name, infer_type)
    if infer_type != "string" and infer_type != "mixed":
        logging.info("try to cast type to %s", infer_type)
        return col

    try_to_date = pd.to_datetime(col, errors="coerce", exact=False)
    date_na_cnt = (pd.isna(try_to_date)).sum()
    logger.info("date_na_cnt is %s", date_na_cnt)
    try_to_int = pd.to_numeric(col, errors="coerce")
    int_na_cnt = (pd.isna(try_to_int)).sum()
    logger.info("int_na_cnt is %s", int_na_cnt)

    if date_na_cnt / len(col) < 0.05:
        return try_to_date
    if int_na_cnt / len(col) < 0.05:
        return try_to_int

    if len(col.unique()) / len(col) < 0.5:
        return pd.Categorical(col)

    all_possible = {
        date_na_cnt: try_to_date,
        int_na_cnt: try_to_int,
    }

    sorted_all = sorted(all_possible.items())
    na_cnt, most_not_na = sorted_all[0]
    end_time = time.time()
    logger.info("col infer process for %s: %d", col.name, end_time - start_time)
    if na_cnt / len(col) < 0.2:  # the na is less than 10%
        return most_not_na
    else:
        return col


def infer_df(df: pd.DataFrame):
    processed = pd.DataFrame()
    for col in df.columns:
        processed[col] = infer_col(df[col])
    return processed


def infer_col_wrapper(args):
    col, df_col = args
    return col, infer_col(df_col)


def infer_df_parallel(df: pd.DataFrame):
    processed = pd.DataFrame()
    with Pool() as pool:
        args = [(col, df[col]) for col in df.columns]
        results = pool.map(infer_col_wrapper, args)
        for col, result in results:
            processed[col] = result
    return processed


safe_namespace = {
    "math": math,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "str": str,
    "int": int,
    "float": float,
    "len": len,
    "pow": pow
}


def process_operation_apply_script(
    prev_df: pd.DataFrame, col: str, raw_script: str
) -> pd.DataFrame:
    prev_df[col] = prev_df[col].apply(
        lambda x: eval(raw_script, safe_namespace, {"x": x})
    )  # TODO better secure code
    return prev_df


def process_operation_cast_to(
    prev_df: pd.DataFrame, col: str, operation_type: str
) -> pd.DataFrame:
    match operation_type:
        case "cast_to_numeric":
            prev_df[col] = pd.to_numeric(prev_df[col], errors="coerce")
        case "cast_to_string":
            prev_df[col] = prev_df[col].apply(str)
        case "cast_to_datetime":
            prev_df[col] = pd.to_datetime(prev_df[col], errors="coerce")
        case "cast_to_boolean":
            prev_df[col] = prev_df[col].apply(bool)
    return prev_df


def process_operation_fill_null(
    prev_df: pd.DataFrame, col: str, to_fill: str
) -> pd.DataFrame:
    col_dtype = prev_df[col].dtype
    # Convert the 'to_fill' value to the type of the column
    if col_dtype == "object":
        to_fill_converted = str(to_fill)
    elif col_dtype == "int":
        to_fill_converted = int(to_fill)
    elif col_dtype == "float":
        to_fill_converted = float(to_fill)
    elif col_dtype == "datetime64[ns]":
        to_fill_converted = pd.to_datetime(to_fill)
    else:
        raise TypeError("Unsupported column data type")
    prev_df[col].fillna(to_fill_converted, inplace=True)
    return prev_df


def map_df_to_json(df: pd.DataFrame) -> str:
    return df.to_json(orient="table")


def create_dataframe_async(df: pd.DataFrame, dataframe_id: str, version_id: str):
    try:
        processed_data = infer_df_parallel(df)
        upload_dataframe(dataframe_id, version_id, processed_data)
        update_status(dataframe_id, version_id, ProcessStatus.PROCESSED)
    except Exception as e:
        logger.error("exception during create_dataframe_async, %s", e.__cause__)
        update_status(dataframe_id, version_id, ProcessStatus.FAIL)


def process_dataframe_async(
    df: pd.DataFrame,
    dataframe_id: str,
    updated_version_id: str,
    operation_type: str,
    column: str,
    raw_script: str | None = None,
    to_fill: str | None = None,
):
    try:
        if operation_type == OperationType.APPLY_SCRIPT:
            processed_dataframe = process_operation_apply_script(df, column, raw_script)
        elif operation_type == OperationType.FILL_NULL:
            processed_dataframe = process_operation_fill_null(df, column, to_fill)
        else:
            processed_dataframe = process_operation_cast_to(df, column, operation_type)
        upload_dataframe(dataframe_id, updated_version_id, processed_dataframe)
        update_status(dataframe_id, updated_version_id, ProcessStatus.PROCESSED)
    except Exception as e:
        logger.error("exception during process_dataframe_async, %s", e.__cause__)
        update_status(dataframe_id, updated_version_id, ProcessStatus.FAIL)

if __name__ == "__main__":
    mixed_data = {
        "A": [
            "2022-01-01",
            "2022-02-01",
            "bad data",
            "2022-03-05",
            "2022-03-07",
            "2022-03-05",
            "2022-03-07",
        ],
        # 'B': ['1', '2', '3', '7', '8', 'bad data', '10'],
        # 'C': ['a', 'b', 'a', 'bad data', 'a', 'b', 'a'],
        # 'D': [True, False, True, False, True, 'bad data', False],
        # 'E': ['Hello', 'its', 'bad data', 'klur', 'world', 'happy', 'coding']
    }
    mixed_df = pd.DataFrame(mixed_data)
    result = infer_df(mixed_df)
    print(result.dtypes)
    print(result["A"])
    # print(mixed_df['D'].astype(bool))
