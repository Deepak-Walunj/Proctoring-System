# from backend import client
# from client import dbclient

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
import client
from client import database
from bson import ObjectId

def convert_objectid_to_string(data):
    """
    Recursively convert ObjectId fields to strings in a dictionary or list.
    """
    if isinstance(data, list):
        return [convert_objectid_to_string(item) for item in data]
    elif isinstance(data, dict):
        return {key: (str(value) if isinstance(value, ObjectId) else convert_objectid_to_string(value))
                for key, value in data.items()}
    return data

db=database()
arr = {
    "domain": "data Analytics",
    "questionSet": [
        {
            "question": "What is HTML?",
            "answer": "It is a hypertext markup language."
        },
        {
            "question": "What is CSS?",
            "answer": "It is a cascading style sheet."
        }
    ],
    "list":[
        {
            "name":"sanika",
            "score":"70",
            "rank":7
        }
    ]
}

def check_duplicate_viva(nameofviva, domain):
    print("cheking duplicate ")
    collection = db['interview']
    try:
        existing_viva = collection.find_one({
            "nameofviva": nameofviva,
            "domain": domain
        })
        if existing_viva:
            # print("true")
            return True
        else:
            return False
        
    except Exception as e:
        print("Error in check_duplicate_viva: ", e)
        return False 
    
def createInterview(arr):
    print(arr)
    collection = db['interview']
    try:
        res=collection.insert_one(arr)
        print("document insertion completed...")
        return res
    except Exception as e:
        print("error in db.py: " , e) 
        return "error"
    
    # print(list(collection.find({})))
# print(creatInterview(arr))
filter={}

def listInterview(filter):
    collection=db["interview"]
    try:
        res=collection.find(filter)
        
        return list(res)
    except Exception as e:
        print("error in db.py: " ,e)
        return "error"
    
def getListFromInterview(id):
    print(id)
    collection=db["viva_reports"]
    try:
        res=collection.find({'vivaID':id})
        # print(res["list"])
        lst=[]
        for i in res:
            data={
                'name':i['name'],
                'Score':i['Score'],
                'rank':i['rank'],
            }
            lst.append(data)
        return lst
    except KeyError:
        print("The key 'list' does not exist in the arr object.")
        return "error"
    
# print(getListFromInterview('78BB1S'))

# filter={"domain": "data Analytics"}
# print(listInterview(filter))

def updateTimer(vivaID,newtime):
    collection=db["interview"]
    try:
        res=collection.update_one({"vivaID":vivaID},{'$set':{'timeforthinking':newtime}})
        print(res)
        return res
    except Exception as e:
        print("error in db.py: ", e)

def updateStatus(vivaID,status):
    collection=db["interview"]
    try:
        res=collection.update_one({"vivaID":vivaID},{'$set':{'status':status}}) 
        print(res)
        return res
    except Exception as e:
        print("error in db.py: ", e)


def updateSetOfQuestions(vivaID,questionSet):
    collection=db["interview"]
    try:
        res=collection.update_one({"vivaID":vivaID},{'$set':{'questionSet':questionSet}})
        print(res)
        return res
    except Exception as e:
        print("error in db.py: ", e)

def deleteviva(vivaID):
    collection=db["interview"]
    try:
        res=collection.delete_one({'vivaID':vivaID})
        print(res)
        return res
    except Exception as e:
        print("error in db.py: ", e)


def getIndividualData(id , name):
    print(id)
    collection=db["viva_reports"]
    try:
        res=collection.find_one({'vivaID':id,'name':name})
        
        data={
                'name':res['name'],
                'Score':res['Score'],
                'rank':res['rank'],
                'feedback':res['feedback'],
                'providedQAndA':res['providedQAndA'],
                'videoID':res['videoID']
            }

        return data
    except KeyError:
        print("The key 'list' does not exist in the arr object.")
        return "error"

def getIssuesData():
    collection = db["candidate_issue"]
    try:
        res = collection.find({})
        lst = []
        for i in res:
            # Use .get() to handle cases where the key might be missing
            data = {
                'name': i.get('name', 'N/A'),  # Default to 'N/A' if 'name' is missing
                'issue': i.get('issue', 'N/A'),  # Default to 'N/A' if 'issue' is missing
                'date_time': i.get('date_time', 'N/A'),  # Default to 'N/A' if 'date_time' is missing
            }
            lst.append(data)
        return lst
    except KeyError:
        print("There was an issue with accessing keys in the MongoDB document.")
        return "error"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "error"

