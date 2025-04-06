# from backend import client
# from client import dbclient

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from client import database
from bson import ObjectId
import math

db=database()


def getQuestionSet(id):
    collection = db['interview']
    try:
        res = collection.find_one({'vivaID': id})
        data = []
        for i in res["questionSet"]:
            difficulty = i.get('difficulty', 'nan')
            try:
                if isinstance(difficulty, str) and difficulty.lower() == 'nan':
                    difficulty = float('nan')  # Convert 'nan' string to actual NaN
                else:
                    difficulty = float(difficulty)  # Ensure it's a float
            except (ValueError, TypeError):
                difficulty = float('nan')
            dt = {
                'question': i['question'],
                'answer': i['answer'],
                'difficulty': 'not available' if math.isnan(difficulty) else i['difficulty'],
                'NOS':i['NOS']
            }
            data.append(dt) 
        print(data)  
        return data, res["NOS_count"],res["timeforthinking"] ,res["domain"]
    except Exception as e:
        print("Error in db.py:", e)
        return str(e)



def listInterview(filter):
    collection=db["interview"]
    try:
        res=collection.find(filter)
        return list(res)
    except Exception as e:
        print("error in db.py: " ,e)
        return e
    
filter={}


def dashboard(name):
    collection = db['interview']
    try:
        res=collection.find({})
        data=[]
        for i in list(res):
            for j in i['list']:
                # print(j['name'])
                if(j['name']==name):
                    d={
                        "domain":i['domain'],
                        'Score':j["Score"],
                        'rank':j['rank']
                    }
                    data.append(d)
        return data
    except Exception as e:
        print("error in db.py: ",e)



def addCandidateToList(id,entry):
    collection=db['interview']
    try:
        res = collection.update_one({"vivaID":id},{"$push":{"list":entry}})
        print("entry added successfully")
        return res 
    except Exception as e :
        print("error in dy.py: ",e) 

def addCadidatesToVivaReport(entry):
    collection=db['viva_reports']
    col=db["interview"]

    try:
        viva=col.find_one({"vivaID":entry['vivaID']})
        print(viva)
        if viva['status']=='Inactive':
            return "viva is currently not active"
        doc=collection.find_one({"vivaID":entry['vivaID'],"name":entry['name']})
        if doc:
            return "viva already given by user"
        res = collection.insert_one(entry)
        print("entry added successfully")
        return "user added for viva" 
    except Exception as e :
        print("error in dy.py: ",e) 



def addFeedbackToList(id, name, questions):
    print("function is called")
    collection = db['interview']
    try:
        # Find the document with the given _id and name in the list
        document = collection.find_one({"vivaID": id, "list.name": name})
        if document:
            print("Document found:") 
            res = collection.update_one(
                {"vivaID": id, "list.name": name},  # Match the document and user
                {"$push": {"list.$.providedQAndA": questions}}  # Append the new question to providedQAndA
            )
            if res.modified_count > 0:
                return {"status": "success", "message": "Feedback added successfully."}
            else:
                return {"status": "failure", "message": "No changes were made."}
        else:
            print("No matching document found for user:", name)
            return {"status": "failure", "message": "Username not found."}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def newaddFeedbackToList(id, name, questions):
    print("function is called")
    collection = db['viva_reports']
    try:
        # Find the document with the given _id and name in the list
        document = collection.find_one({"vivaID": id, "name": name})
        if document:
            print("Document found:") 
            res = collection.update_one(
                {"vivaID": id, "name": name},  # Match the document and user
                {"$push": {"providedQAndA": questions}}  # Append the new question to providedQAndA
            )
            if res.modified_count > 0:
                return {"status": "success", "message": "Feedback added successfully."}
            else:
                return {"status": "failure", "message": "No changes were made."}
        else:
            print("No matching document found for user:", name)
            return {"status": "failure", "message": "Username not found."}
    
    except Exception as e:
        return {"status": "error", "message": str(e)} 
    

def fetchAllInfo(id, name):
    try:
        collection = db['interview']
        document = collection.find_one({"vivaID":id})
        if not document:
            return f"No document found with the id: {id}"
        matching_entries = [
            {**entry, "domain": document.get("domain", "")}  
            for entry in document.get("list", [])
            if entry.get("name") == name
        ]
        return matching_entries if matching_entries else f"No entries found for the name: {name}"
    except Exception as e:
        return f"Error: {str(e)}"
    



def fetch_question(doc_id, name, question_id):
    try:
        collection = db['interview']
        document = collection.find_one({"_id": ObjectId(doc_id)})
        if not document:
            return "No document found"
        user_entry = next((entry for entry in document.get("list", []) if entry.get("name") == name), None)
        if not user_entry:
            return "No entry found for the name"
        if 0 <= question_id < len(user_entry.get("providedQAndA", [])):
            return user_entry["providedQAndA"][question_id]
        else:
            return "Question ID is out of range"
    except Exception as e:
        return f"Error: {str(e)}"



def fetchListOfIndividuaLReport(id, name):
    collection = db['viva_reports']
    try:
        document = collection.find_one({"vivaID": id, "name":name})
        if not document:
            return f"No document found with the id: {id} and name:{name}"
        # user_entry = next((entry for entry in document.get("list", []) if entry.get("name") == name), None)
        test=document['providedQAndA']
        # if not user_entry:
        #     return "No entry found for the name"
        # else:
        #     test=user_entry['providedQAndA']
        #     ls=[]
            # for i in test:
            #     ls.append({"feedback":i['feedback'],"question":i['question'],"user_answer":i['userans']})
        return test
    except Exception as e:
        return f"error in db.py: {str(e)}"
    
def saveFinalReport(id,name,report):
    collection=db["viva_reports"]
    totalScore=calculateTotalScore(id,name)
    
    try:
        res1=collection.update_one({"vivaID": id,"name": name},{"$set":{"Score":totalScore}})
        res2=collection.update_one({"vivaID": id,"name": name},{"$set":{"feedback":report}})
        # print(res2)
        return res2
    except Exception as e:
        return f"error in db.py: {str(e)}"
    
def calculateTotalScore(id, name):
    collection = db['viva_reports']
    try:
        document = collection.find_one({"vivaID": id,"name":name})
        if not document:
            return f"No document found with the id: {id}"
        # user_entry = next((entry for entry in document.get("list", []) if entry.get("name") == name), None)
        test=document['providedQAndA']
        total_score=0;
        for i in test:
                # ls.append({"feedback":i['feedback'],"question":i['question'],"user_answer":i['userans']})
            total_score+=i['Analysis']['overall score']
        total_score/=len(document['providedQAndA'])
        return total_score
    except Exception as e:
        return f"error in db.py: {str(e)}"



def addissue(doc):
    collection=db['candidate_issue']
    try:
        res=collection.insert_one(doc)
        return res
    except Exception as e:
        return 'error'


def getuserdetails(username):
    collection = db['interviewee'] 
    try:
        user = collection.find_one({"username": username})
        # print(user)
        if user:
            print("user founded")
            data={
            "username":user['username'],
            "email":user['email'],
            "date_registered":user['date_registered'],
            "name":user['name'],
            "img":user['img'], 
            "gender":user['gender'],
            }
            return data  
        return None
    except Exception as e:
        return None

def get_all_users():
    collection = db['interviewee'] 
    try:
        # Fetch all users from the collection
        users = collection.find({})
        
        # Prepare the list to hold user data
        data = []
        
        for user in users:
            # Append user details to the list
            data.append({
                "username": user.get('username'),
                "name" : user.get('name'),
                "email": user.get('email'),
            })
        
        # Return the user data
        return data
    except Exception as e:
        # Log the error for debugging
        print(f"Error fetching users: {e}")
        return None

def saveVideoID(vivaID,username,videoID):
    collection=db["viva_reports"]
    try:
        doc=collection.find_one({"vivaID": vivaID,"name":username})

        if doc:
            print("found doc")
            res=collection.update_one({"vivaID": vivaID,"name":username},{"$set":{"videoID":videoID}})
            return res
        
    except Exception as e:
        return "error"