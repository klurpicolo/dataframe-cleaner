from .views import ProcessDataFrameView


routes = [
    {"regex": r"rest", "viewset": ProcessDataFrameView, "basename": "Rest"},
]
