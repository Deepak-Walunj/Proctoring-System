import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db=client["CandidateFace"]
coll=db["Faces"]

def login(name):
    try:
        doc={"name":name}
        reterived_doc=coll.find_one(doc)
        if reterived_doc:
            print("Login Successfully!....\n")
            return True, reterived_doc
        else:
            print("No such entry for " + name)
            return False, None
    except Exception as e:
        print(e)
        return False, None
    
if __name__ == "__main__":
    name=input("Enter name for login\n")
    login(name)