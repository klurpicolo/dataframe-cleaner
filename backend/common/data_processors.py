import logging
import math
import time
from multiprocessing import Pool

import pandas as pd

from .minio_client import upload_dataframe
from .mongo_client import update_status
from .processing_enum import OperationType, ProcessStatus


logger = logging.getLogger(__name__)

NEED_MORE_REFINEMENT = ["string", "mixed", "integer"]

DATE_NA_THRESHOLD = 0.1
INT_NA_THRESHOLD = 0.1
TIMEDELTA_NA_THRESHOLD = 0.1
BOOL_NA_THRESHOLD = 0.2
CATEGORY_THRESHOLD = 0.4

ACCEPTABLE_NA_THRESHOLD = 0.5


def infer_col(col: pd.Series) -> pd.Series:
    """
    *** This is not the ultimate solution as it still require a lot of refinement. ***
    Infer type
    This method'll try to convert the pandas series into user friendly type

    - boolean

    Convert the following bool compatible
    "true", "yes", "1" to True
    "false", "no", "0" to False
    if all row process successfully, return as bool series

    - datetime, timedelta, int, complex

    convert with respective pandas type
    also add more support on non standard
      - delta weeks, months, years
      - some datetime format

    - category

    Check cardinality before apply

    - string

    only if non of above satisfy conditions.

    """

    start_time = time.time()
    infer_type = pd.api.types.infer_dtype(col, skipna=True)
    logger.info("infer type from pandas col %s is %d", col.name, infer_type)
    if infer_type not in NEED_MORE_REFINEMENT:
        logging.info("pandas cast type to %s", infer_type)
        return col

    try_to_date = pd.to_datetime(col, errors="coerce", format="mixed", dayfirst=True)
    date_na_cnt = (pd.isna(try_to_date)).sum()
    logger.info("date_na_cnt is %s", date_na_cnt)
    try_to_int = infer_int(col)
    int_na_cnt = (pd.isna(try_to_int)).sum()
    logger.info("int_na_cnt is %s", int_na_cnt)
    try_to_timedelta = pd.to_timedelta(col, errors='coerce')
    timedelta_na_cnt = (pd.isna(try_to_timedelta)).sum()
    try_to_boolean = infer_boolean(col)
    boolean_na_cnt = (pd.isna(try_to_boolean)).sum()

    if int_na_cnt / len(col) < INT_NA_THRESHOLD:
        return try_to_int
    if boolean_na_cnt / len(col) < BOOL_NA_THRESHOLD:
        return try_to_boolean
    if date_na_cnt / len(col) < DATE_NA_THRESHOLD:
        return try_to_date
    if timedelta_na_cnt / len(col) < TIMEDELTA_NA_THRESHOLD:
        return try_to_timedelta

    if len(col.unique()) / len(col) < CATEGORY_THRESHOLD:
        return pd.Categorical(col)

    all_possible = {
        '1nt': {
            'na_cnt' : int_na_cnt,
            'series': try_to_int,
        },
        'date': {
            'na_cnt': date_na_cnt,
            'series': try_to_date,
        },
        'timedelta': {
            'na_cnt': timedelta_na_cnt,
            'series': try_to_timedelta,
        },
        'bool': {
            'na_cnt': boolean_na_cnt,
            'series': try_to_boolean,
        },
    }

    sorted_all = sorted(all_possible.items(), key=lambda x: x[1]['na_cnt'])

    _, na_cnt_series = sorted_all[0]
    na_cnt = na_cnt_series['na_cnt']
    most_not_na = na_cnt_series['series']
    end_time = time.time()
    logger.info("col infer process for %s: %d", col.name, end_time - start_time)
    if na_cnt / len(col) < ACCEPTABLE_NA_THRESHOLD:
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


def infer_boolean(col: pd.Series) -> pd.Series | None:
    true_variants = ["true", "yes", "t", "1"]
    false_variants = ["false", "no", "f", "0"]
    def try_bool(data):
        lower = str(data).lower()
        if lower in true_variants:
            return True
        if lower in false_variants:
            return False
        return pd.NA

    defer_bool = col.apply(try_bool).astype("boolean")
    return defer_bool

def infer_int(col: pd.Series) -> pd.Series | None:
    to_trip_chars = ["\"", "'"]
    to_replace = ","
    def try_int(data):
        for to_trim_char in to_trip_chars:
            trimed = str(data).lstrip(to_trim_char)
            trimed = trimed.rstrip(to_trim_char)

        trimed = trimed.replace(to_replace, "")
        try:
            int_val = int(trimed)
            return int_val
        except:
            return pd.NA

    defer_int = col.apply(try_int).astype(pd.Int64Dtype())
    return defer_int

SAFE_NAMESPACES = {
    "math": math,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "str": str,
    "int": int,
    "float": float,
    "len": len,
    "pow": pow,
    "split": str.split,
}


def process_operation_apply_script(
    prev_df: pd.DataFrame, col: str, raw_script: str
) -> pd.DataFrame:
    """Return the data frame that processed by raw_script as lambda function.
    The support method is list in SAFE_NAMESPACES.
    """
    prev_df[col] = prev_df[col].apply(
        lambda x: eval(raw_script, SAFE_NAMESPACES, {"x": x})
    )
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
        case "cast_to_timedelta":
            prev_df[col] = pd.to_timedelta(prev_df[col], errors="coerce")
        case "cast_to_boolean":
            prev_df[col] = prev_df[col].apply(bool)
        case "cast_to_category":
            prev_df[col] = pd.Categorical(prev_df[col])
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
    elif col_dtype == "timedelta64[ns]":
        to_fill_converted = pd.Timedelta(to_fill)
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
        logger.error("exception during process_dataframe_async, %s", e)
        update_status(dataframe_id, updated_version_id, ProcessStatus.FAIL)
