from .views import ProcessDataFrameView, RestViewSet


routes = [
    {"regex": r"rest", "viewset": RestViewSet, "basename": "Rest"},
    {"regex": r"rest", "viewset": ProcessDataFrameView, "basename": "Rest"},
]
