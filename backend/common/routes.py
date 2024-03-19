from .views import RestViewSet, SaveMongo, FileUploadView, ProcessDataFrameViewV2


routes = [
    {"regex": r"rest", "viewset": RestViewSet, "basename": "Rest"},
    {"regex": r"rest", "viewset": SaveMongo, "basename": "Rest"},
    {"regex": r"rest", "viewset": FileUploadView, "basename": "Rest"},
    {"regex": r"rest", "viewset": ProcessDataFrameViewV2, "basename": "Rest"},
]
