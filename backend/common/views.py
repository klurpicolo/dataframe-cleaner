import json
import logging
import multiprocessing
import time
import traceback
import uuid
from io import BytesIO

from django.http import FileResponse
from django.views import generic

import pandas as pd
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .data_processors import (
    create_dataframe_async,
    map_df_to_json,
    process_dataframe_async,
)
from .minio_client import get_dataframe
from .mongo_client import (
    get_dataframe_by_id,
    insert_version,
    save_to_mongo,
)
from .processing_enum import OperationType, ProcessStatus


logger = logging.getLogger(__name__)


class IndexView(generic.TemplateView):
    template_name = "common/index.html"


class ProcessDataFrameView(viewsets.ViewSet):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

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
                {"message": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if file_obj.name.endswith(".csv"):
                df = pd.read_csv(file_obj)
            elif file_obj.name.endswith(".xls") or file_obj.name.endswith(".xlsx"):
                df = pd.read_excel(file_obj)
            else:
                return Response(
                    {
                        "message": "Unsupported file type, only support .csv, .xls, .xlsx"
                    },
                    status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                )

            init_version_id = str(uuid.uuid4())
            to_save = {
                "dataframe_id": str(uuid.uuid4()),
                "versions": [
                    {
                        "version_id": init_version_id,
                        "operation": OperationType.INITIALIZE,
                        "status": ProcessStatus.PROCESSING,
                    }
                ],
            }
            save_to_mongo(to_save)

            process = multiprocessing.Process(
                target=create_dataframe_async,
                args=(df, to_save["dataframe_id"], init_version_id),
            )
            process.start()

            end_time = time.time()
            logger.info("Request process time: %s", end_time - start_time)
            response = {
                "dataframe_id": to_save["dataframe_id"],
                "version_id": init_version_id,
                "status": ProcessStatus.PROCESSING,
            }
            return Response(response, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error("exception %s", e)
            traceback.print_exception(e)
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="dataframes/(?P<dataframe_id>[^/.]+)/process-async",
    )
    def process_dataframe_async(self, request, *args, **kwargs):
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
                    "message": "Missing parameters. Please provide all required parameters."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_script = operation.get("script", None)
        to_fill = operation.get("to_fill", None)

        updated_version_id = str(uuid.uuid4())
        update = {
            "version_id": updated_version_id,
            "operation": operation_type,
            **({"script": raw_script} if raw_script is not None else {}),
            **({"to_fill": to_fill} if to_fill is not None else {}),
            "column": column,
            "status": ProcessStatus.PROCESSING,
        }
        insert_version(dataframe_id, update)

        prev_dataframe = get_dataframe(dataframe_id, version_id)

        process = multiprocessing.Process(
            target=process_dataframe_async,
            args=(
                prev_dataframe,
                dataframe_id,
                updated_version_id,
                operation_type,
                column,
                raw_script,
                to_fill,
            ),
        )
        process.start()

        response_data = {
            "dataframe_id": dataframe_id,
            "previous_version_id": version_id,
            "version_id": updated_version_id,
            "column": column,
            "operation_type": operation_type,
            "status": ProcessStatus.PROCESSING,
        }
        return Response(response_data, status=status.HTTP_202_ACCEPTED)

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
                    "message": "Missing parameters. Please provide all required parameters."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        dataframe_meta = get_dataframe_by_id(dataframe_id)
        if dataframe_meta is None:
            return Response(
                {"message": "Dataframe id is not found"},
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
        limit_size = 100000
        dataframe_id = kwargs.get("dataframe_id")
        version_id = kwargs.get("version_id")
        dataframe = get_dataframe(dataframe_id, version_id)
        # limit code display on FE
        json_processed_data = json.loads(map_df_to_json(dataframe[:limit_size]))
        actual_size = len(dataframe)
        response = {
            "dataframe_id": dataframe_id,
            "version_id": version_id,
            "data": json_processed_data,
            "actual_size": actual_size,
            "limit_size": limit_size if actual_size > limit_size else actual_size,
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
