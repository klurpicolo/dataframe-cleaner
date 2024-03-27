from .views import ProcessDataFrameView


routes = [
    {"regex": r"", "viewset": ProcessDataFrameView, "basename": "dataframes-async"},
]
