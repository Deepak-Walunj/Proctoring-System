import pymongo
from pymongo import MongoClient



def database():
    client=MongoClient("mongodb+srv://sachishinde20:04QF2cJsYsv92ePB@cluster0.0tz5h.mongodb.net/")
    print("connecting successfully completed..")
    db = client["AssesmentPlatform"]
    return db