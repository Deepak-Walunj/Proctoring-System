import pymongo
import base64
from PIL import Image
from io import BytesIO
import cv2 as cv
import io

class DatabaseOps:
    def __init__(self):
        self.client=pymongo.MongoClient("mongodb://localhost:27017/")
        self.db=self.client["CandidateFace"]
        self.coll=self.db["Faces"]
        
    def is_db_NotEmpty(self):
        status=False
        toast=""
        try:
            res=self.coll.find()
            all_docs=list(res)
            if len(all_docs) == 0:
                toast="Database is empty!"
                return status, toast
            else:
                status=True
                toast="Database is not empty!"
                return status, toast
        except Exception as e:
            status=False
            toast=f"[Error] checking database: {e}"
            return status, toast

    def take_photo_from_database(self, name):
        dbIstatus=False
        dbItoast=""
        try:
            data=self.coll.find_one({"name": name}, {"_id":0, "data": 1})
            if data is not None:
                image_data=data["data"]
                if isinstance(image_data, str):
                    image_data = base64.b64decode(image_data)
                pil_image = Image.open(BytesIO(image_data))
                dbItoast="From student verification, image taken from the database successfully"
                dbIstatus=True
                return pil_image, dbIstatus, dbItoast
            else:
                dbItoast="Couldn't find the student!"
                dbIstatus=False
                return None, dbIstatus, dbItoast
        except Exception as e:
            dbIstatus=False
            dbItoast=f"[Error] retrieving image from database: {e}"
            return None, dbIstatus, dbItoast

    def registerStudent(self, name, image):
        status=False
        toast=""
        try:
            _, buffer = cv.imencode('.jpg', image)
            image_byte = io.BytesIO(buffer)
            im = Image.open(image_byte)
            image_byte = io.BytesIO()
            im.save(image_byte, format='PNG')
            doc = {
                "name": name,
                "data": image_byte.getvalue()
            }
            doc_id = self.coll.insert_one(doc).inserted_id
            status=True
            toast="Face registered successfully."
            return doc_id, status, toast
        except Exception as e:
            status=False
            toast=f"[Error] face registration: {e}"
            return None, status, toast

    def to_view_specific_student(self, name):
        status=False
        toast=""
        try:
            doc={"name": name}
            doc_retrived=self.coll.find_one(doc)
            if doc_retrived:
                status=True
                toast="Student documnet found!\n"
                return status, doc_retrived, toast
            else:
                status=False
                toast="No such student found!"
                return status, None, toast
        except Exception as e:
            status=False
            toast=f"[Error] retrieving student document: {e}"
            return status, None, toast

    def to_view_all_students(self):
        status=False
        toast=""
        try:
            all_docs=self.coll.find()
            status=True
            toast="All student documents retrieved successfully!"
            return status, all_docs, toast
        except Exception as e:
            status=False
            toast=f"[Error] retrieving all student documents: {e}"
            return status, all_docs, toast

    def to_delete_all_students(self):
        status=False
        toast=""
        try:
            deleted=self.coll.delete_many({})
            status=True
            toast=f"{deleted.deleted_count} documents deleted."
            return status, toast
        except Exception as e:
            status=False
            toast=f"[Error] deleting all student documents: {e}"
            return status, toast

    def to_delete_a_student(self, name):
        status=False
        toast=""
        try:
            cond, doc_retrived, toast=self.to_view_specific_student(name)
            if cond:
                status=True
                doc={"name":name}
                self.coll.delete_one(doc)
                toast=f"Student {name} deleted successfully."
                return status, toast
            else:
                status=False
                toast="Deletion unsuccessfull!"
                return status, toast
        except Exception as e:
            status=False
            toast=f"[Error] deleting student document: {e}"
            return status, toast

if __name__=="__main__":
    choice=int(input("Enter\n1) for registeration\n2) for student image\n3) to view a specific student\n4) to view all students\n5) to delete all students\n6) to delete a student\n7) Check database\n"))
    dbOps=DatabaseOps()
    match choice:
        case 1:
            name=input("Enter name for registeration: ")
            image=cv.imread("test.jpg")
            doc_id=dbOps.registerStudent(name, image)
            print(doc_id)
        case 2:
            name=input("Enter the name of the student: ")
            image, imageStatus, imageToast=dbOps.take_photo_from_database(name)
            print(f"Image status :{imageStatus}")
            print(f"Image toast :{imageToast}")
            if imageStatus:
                image.show()
            else:   
                print("Image not found or error occurred.")
        case 3:
            name=input("Enter the name of the student: ")
            status, doc_retrived, toast=dbOps.to_view_specific_student(name)
            print(toast)
            if status:
                print(doc_retrived)
        case 4:
            status, all_docs, toast=dbOps.to_view_all_students()
            print(toast+"\nNames:")
            if status:
                for doc in all_docs:
                    print(doc.get("name", "No name found"))
        case 5:
            status, toast=dbOps.to_delete_all_students()
            print(toast)
        case 6:
            name=input("Enter the name of the student to delete: ")
            status, toast=dbOps.to_delete_a_student(name)
            print(toast)
        case 7:
            dbOps=DatabaseOps()
            status, toast=dbOps.is_db_NotEmpty()
            print(toast)
        case _:
            print("Invalid choice. Please try again.")