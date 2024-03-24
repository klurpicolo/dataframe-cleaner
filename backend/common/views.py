import json
import logging
import time
import traceback
import uuid
from io import BytesIO

from django.http import FileResponse
from django.views import generic

import pandas as pd
from celery import shared_task
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .data_processors import (
    infer_df,
    map_df_to_json,
    process_operation_apply_script,
    process_operation_cast_to,
    process_operation_fill_null,
)
from .minio_client import get_dataframe, upload_dataframe
from .mongo_client import get_dataframe_by_id, insert_version, save_to_mongo, update_status


logger = logging.getLogger(__name__)

class IndexView(generic.TemplateView):
    template_name = "common/index.html"


class RestViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path="rest-check",
    )
    def rest_check(self, request):
        return Response(
            {
                "result": "This message comes from the backend. "
                "If you're seeing this, the REST API is working!"
            },
            status=status.HTTP_200_OK,
        )


@shared_task
def process_dataframe_async(df: pd.DataFrame, dataframe_id: str, version_id: str):
    processed_data = infer_df(df)
    upload_dataframe(dataframe_id, version_id, processed_data)
    update_status(dataframe_id, version_id, "processed")

class ProcessDataFrameView(viewsets.ViewSet):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="dataframes",
    )
    def create_dataframe(self, request, *args, **kwargs):
        start_time = time.time()
        file_obj = request.FILES["file"]

        if not file_obj:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if file_obj.name.endswith(".csv"):
                df = pd.read_csv(file_obj)
            elif file_obj.name.endswith(".xls") or file_obj.name.endswith(".xlsx"):
                df = pd.read_excel(file_obj)
            else:
                return Response(
                    {"error": "Unsupported file type"},
                    status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                )

            processed_data = infer_df(df)
            init_version_id = str(uuid.uuid4())
            to_save = {
                "dataframe_id": str(uuid.uuid4()),
                "versions": [
                    {"version_id": init_version_id, "operation": "initialize"}
                ],
            }
            save_to_mongo(to_save)
            upload_dataframe(to_save["dataframe_id"], init_version_id, processed_data)
            json_processed_data = json.loads(map_df_to_json(processed_data))

            end_time = time.time()
            logger.info(f"Request process time: {end_time - start_time}")
            response = {
                "dataframe_id": to_save["dataframe_id"],
                "version_id": init_version_id,
                "data": json_processed_data,
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"exception {e}")
            traceback.print_exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # save status to mongo first
    # > then return to client with status wait
    # > client setup long pooling to get data later
    # async process the pandas and update mongo later
    # > then update status from processing to processed
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="dataframes-async",
    )
    def create_dataframe_async(self, request, *args, **kwargs):
        start_time = time.time()
        file_obj = request.FILES["file"]

        if not file_obj:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if file_obj.name.endswith(".csv"):
                df = pd.read_csv(file_obj)
            elif file_obj.name.endswith(".xls") or file_obj.name.endswith(".xlsx"):
                df = pd.read_excel(file_obj)
            else:
                return Response(
                    {"error": "Unsupported file type"},
                    status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                )

            init_version_id = str(uuid.uuid4())
            to_save = {
                "dataframe_id": str(uuid.uuid4()),
                "versions": [
                    {"version_id": init_version_id, "operation": "initialize", "status": "processing"}
                ],
            }
            save_to_mongo(to_save)
            process_dataframe_async(df, to_save['dataframe_id'], init_version_id)

            end_time = time.time()
            logger.info(f"Request process time: {end_time - start_time}")
            response = {
                "dataframe_id": to_save["dataframe_id"],
                "version_id": init_version_id,
                "status": "processing",
            }
            return Response(response, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error(f"exception {e}")
            traceback.print_exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="dataframes/(?P<dataframe_id>[^/.]+)/process",
    )
    def process_dataframe(self, request, *args, **kwargs):
        dataframe_id = kwargs.get("dataframe_id")
        request_data = request.data
        version_id = request_data.get("version_id", None)
        column = request_data.get("column", None)
        operation = request_data.get("operation", None)
        operation_type = None
        if operation:
            operation_type = operation.get("type", None)

        if None in [dataframe_id, version_id, column, operation, operation_type]:
            return Response(
                {
                    "error": "Missing parameters. Please provide all required parameters."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_script = operation.get("script", None)
        prev_dataframe = get_dataframe(dataframe_id, version_id)
        if operation_type == "apply_script":
            processed_dataframe = process_operation_apply_script(
                prev_dataframe, column, raw_script
            )
        elif operation_type == 'fill_null':
            to_fill = operation.get('to_fill', None)
            processed_dataframe = process_operation_fill_null(
                prev_dataframe, column, to_fill
            )
        else :
            processed_dataframe = process_operation_cast_to(
                prev_dataframe, column, operation_type
            )

        updated_dataframe = json.loads(map_df_to_json(processed_dataframe))

        updated_version_id = str(uuid.uuid4())
        update = {
            "$push": {
                "versions": {
                    "version_id": updated_version_id,
                    "operation": operation_type,
                    **({"script": raw_script} if raw_script is not None else {}),
                    "column": column,
                }
            }
        }

        insert_version(dataframe_id, update)
        upload_dataframe(dataframe_id, updated_version_id, prev_dataframe)

        response_data = {
            "dataframe_id": dataframe_id,
            "previous_version_id": version_id,
            "version_id": updated_version_id,
            "column": column,
            "operation_type": operation_type,
            "data": updated_dataframe,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path="dataframes/(?P<dataframe_id>[^/.]+)",
    )
    def get_dataframe_metadata(self, request, *arg, **kwargs):
        dataframe_id = kwargs.get("dataframe_id")
        if dataframe_id is None:
            return Response(
                {
                    "error": "Missing parameters. Please provide all required parameters."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        dataframe_meta = get_dataframe_by_id(dataframe_id)
        if dataframe_meta is None:
            return Response(
                {
                    "error": "Dataframe id is not found"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(dataframe_meta, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path="dataframes/(?P<dataframe_id>[^/.]+)/versions/(?P<version_id>[^/.]+)",
    )
    def get_dataframe_by_id_and_version(self, request, *args, **kwargs):
        dataframe_id = kwargs.get("dataframe_id")
        version_id = kwargs.get("version_id")
        dataframe = get_dataframe(dataframe_id, version_id)
        json_processed_data = json.loads(map_df_to_json(dataframe))
        response = {
            "dataframe_id": dataframe_id,
            "version_id": version_id,
            "data": json_processed_data,
        }
        return Response(response, status=status.HTTP_201_CREATED)


    @action(
        detail=False,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path="dataframes/(?P<dataframe_id>[^/.]+)/download/(?P<version_id>[^/.]+)",
    )
    def download_dataframe(self, request, *args, **kwargs):
        dataframe_id = kwargs.get("dataframe_id")
        version_id = kwargs.get("version_id")
        dataframe = get_dataframe(dataframe_id, version_id)
        buff = BytesIO()
        dataframe.to_csv(path_or_buf=buff)
        buff.seek(0)
        return FileResponse(buff, filename="processed_data.csv", as_attachment=True)
