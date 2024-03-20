from .views import ProcessDataFrameView, RestViewSet, SaveMongo


routes = [
    {"regex": r"rest", "viewset": RestViewSet, "basename": "Rest"},
    {"regex": r"rest", "viewset": SaveMongo, "basename": "Rest"},
    {"regex": r"rest", "viewset": ProcessDataFrameView, "basename": "Rest"},
]
