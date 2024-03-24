import json
import logging
import math
import time
from multiprocessing import Pool
from typing import Any

import pandas as pd


logger = logging.getLogger(__name__)


def infer_col(raw_dict: dict[Any, Any]) -> str:
    col = pd.Series(raw_dict)
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


def infer_col2(col: pd.Series) -> str:
    start_time = time.time()
    infer_type = pd.api.types.infer_dtype(col, skipna=True)
    logger.info(f"infer type from pandas is {infer_type}")
    if infer_type != "string" and infer_type != "mixed":
        logging.info(f"try to cast type to {infer_type}")
        return col

    try_to_date = pd.to_datetime(col, errors="coerce", exact=False)
    date_na_cnt = (pd.isna(try_to_date)).sum()
    logger.info(f"date_na_cnt is {date_na_cnt}")
    try_to_int = pd.to_numeric(col, errors="coerce")
    int_na_cnt = (pd.isna(try_to_int)).sum()
    logger.info(f"int_na_cnt is {int_na_cnt}")

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
    logger.info(f"Col infer process for {col.name}: {end_time - start_time}")
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


def map_json_to_df(json_str: str) -> pd.DataFrame:
    dump_str = json.dumps(json_str)
    df = pd.read_json(dump_str, orient="table")
    return df


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