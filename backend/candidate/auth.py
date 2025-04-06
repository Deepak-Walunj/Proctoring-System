import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.hashers import make_password, check_password, get_hasher
from client import database
from company.encp import encrypt_and_shorten_student_id,decrypt_student_id
from bson import ObjectId
import datetime 


db = database()
collection=db['interviewee']

def register_user(data):
    try:
        if collection.find_one({'username':data['username']}):
            return "user already exist"
        hash_password=encrypt_and_shorten_student_id(data['password'])
        user_doc={
                "name": data['name'],
                "username": data['username'],
                "email": data['email'],
                "password": hash_password,  
                "img":data["img"],
                "gender":data["gender"],
                "date_registered": datetime.datetime.now().strftime('%d/%m/%y'),              
                
                

        }
        print("adding user")
        res =collection.insert_one(user_doc)
        print("user added succesfully")
        return "user added successfully!"
    except Exception as e:
        print("error in auth.py: ",e)
        return False

    
def getuser(username, password):
    try:
        user = collection.find_one({"username": username})
        # print(user)
        print("hi")

        if user:
            print("user found ")
            print(decrypt_student_id(user['password']))
            # print(make_password(password))
            print(password==decrypt_student_id(user['password']))
            if(password==decrypt_student_id(user['password'])):
                return {"status": "Login successful", "user_id": str(user["_id"])}
            else:
                return {"status": "incorrect password"}
        else:
            return {"status": "User not found"}
    
    except Exception as e:
        print("Error in getuser:", e)
        return {"status": "Error during login"}

