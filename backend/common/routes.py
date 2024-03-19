from .views import RestViewSet, SaveMongo, FileUploadView


routes = [
    {"regex": r"rest", "viewset": RestViewSet, "basename": "Rest"},
    {"regex": r"rest", "viewset": SaveMongo, "basename": "Rest"},
    {"regex": r"rest", "viewset": FileUploadView, "basename": "Rest"},
]
