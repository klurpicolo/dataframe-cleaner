import pymongo


# This isn't not secure, just for sake of setup and prototype.
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["my_mongodb_database"]
collection = db["dataframe_metadata"]

def save_to_mongo(data):
    return collection.insert_one(data)

def get_dataframe_by_id(dataframe_id):
    return collection.find_one({"dataframe_id": dataframe_id}, {'_id': False})

def update_dataframe(dataframe_id, update):
    collection.update_one({"dataframe_id": dataframe_id}, update)

def insert_version(dataframe_id, version_data):
    collection.update_one({"dataframe_id": dataframe_id}, {"$push": {"versions": version_data}})

def update_status(dataframe_id: str, version_id: str, status: str):
    collection.update_one(
        {"dataframe_id": dataframe_id, "versions.version_id": version_id},
        {"$set": {"versions.$.status": status}}
    )
