import json
import uuid

from django.views import generic

import bson
import pandas as pd
import pymongo
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .data_processors2 import infer_df, map_df_to_json, map_json_to_df


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


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["my_mongodb_database"]
collection = db["my_collection"]


class SaveMongo(viewsets.ViewSet):
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="mongo-save",
    )
    def demo_save(self, request):
        saved = collection.insert_one({"data": "klue"})
        return Response(
            {"result": f"{saved}"},
            status=status.HTTP_200_OK,
        )


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # check file format first
    inferred_df = infer_df(df)
    return inferred_df


class FileUploadView(viewsets.ViewSet):
    parser_classes = (MultiPartParser, FormParser)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="dataframes",
    )
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES["file"]
        # Example: Processing CSV file
        df = pd.read_csv(file_obj)

        # Process the data further as needed
        # For example, save to database or perform computations
        processed_data = process_dataframe(df)

        processed_data_dict = processed_data.rename(columns=str).to_json()
        print(f"klur log {len(processed_data_dict)}")
        saved = collection.insert_one(
            {
                "dataframe_id": bson.Binary.from_uuid(uuid.uuid4()),
                "version_id": 1,
                "data": processed_data_dict,
            }
        )

        return Response(processed_data, status=status.HTTP_201_CREATED)


class ProcessDataFrameViewV2(viewsets.ViewSet):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="dataframesv2",
    )
    def create_dataframe(self, request, *args, **kwargs):
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

            processed_data = process_dataframe(df)
            table = json.loads(
                map_df_to_json(
                    processed_data
                )  # TODO Save the data before to json instead
            )
            to_save = {
                "dataframe_id": str(uuid.uuid4()),
                "version_id": str(uuid.uuid4()),
                "data": table,
            }
            saved = collection.insert_one(to_save.copy())
            return Response(to_save, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"exception {e}")
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

        query = {"dataframe_id": dataframe_id, "version_id": version_id}
        prev_dataframe_document = collection.find_one(query)
        prev_dataframe = map_json_to_df(prev_dataframe_document["data"])

        match operation_type:
            case "cast_to_numeric":
                prev_dataframe[column] = pd.to_numeric(
                    prev_dataframe[column], errors="coerce"
                )
            case "cast_to_string":
                prev_dataframe[column] = prev_dataframe[column].apply(str)
            case "cast_to_datetime":
                prev_dataframe[column] = pd.to_datetime(
                    prev_dataframe[column], errors="coerce"
                )
            case "cast_to_boolean":
                prev_dataframe[column] = prev_dataframe[column].apply(bool)

        updated_dataframe = json.loads(map_df_to_json(prev_dataframe))

        updated_version_id = str(uuid.uuid4())
        to_save = {
            "dataframe_id": dataframe_id,
            "version_id": updated_version_id,
            "data": updated_dataframe,
        }
        collection.insert_one(to_save)

        response_data = {
            "dataframe_id": dataframe_id,
            "previous_version_id": version_id,
            "version_id": updated_version_id,
            "column": column,
            "operation_type": operation_type,
            "data": updated_dataframe,
        }

        return Response(response_data)
