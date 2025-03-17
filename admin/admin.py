import pymongo as py
from PIL import Image
import io
import matplotlib.pyplot as plt

client=py.MongoClient("mongodb://localhost:27017/")
db=client["CandidateFace"]
coll=db["Faces"]

def is_db_NotEmpty():
    res=coll.find()
    all_docs=list(res)
    if len(all_docs) == 0:
        print("Database is empty!")
        return False
    else:
        return True

def retriveImage(doc):
    pil_img = Image.open(io.BytesIO(doc['data']))
    plt.imshow(pil_img)
    plt.show()

def to_view_specific_student(name):
    doc={"name": name}
    doc_retrived=coll.find_one(doc)
    if doc_retrived:
        print("Student documnet found!\n")
        return True, doc_retrived
    else:
        print("No such student found!")
        return False, None

def to_view_all_students():
    all_doCS=coll.find()
    for docs in all_doCS:
        print(docs)

def to_delete_all_students():
    deleted=coll.delete_many({})
    print(f"{deleted.deleted_count} documents deleted.")

def to_delete_a_student(name):
    cond=to_view_specific_student(name)
    if cond:
        doc={"name":name}
        coll.delete_one(doc)
        print(f"Student {name} deleted successfully.")
    else:
        print("Deletion unsuccessfull!")

def Admin():
    print("*"*50,"Welcome Admin","*"*50)
    while True:
        try:
            ch=int(input("Enter\n1)To view all documents\n2)To view a student\n3)To delete a student\n4)To delete all students\n5)To logout\n"))
            match ch:
                case 1:
                    cond=is_db_NotEmpty()
                    if cond==True:
                        to_view_all_students()
                        while True:
                            try:
                                to_del=int(input("Enter:\n1)To delete all records form the database!\n2)Quit\n"))
                                match to_del:
                                    case 1:
                                        to_delete_all_students()
                                        continue
                                    case 2:
                                        print("Quitting...")
                                        break
                                    case _:
                                        print("Invalid choice! please enter a valid between 1 & 2.")
                                        continue
                            except (ValueError, NameError, EOFError):
                                print("Admin please enter a valid choice!")
                                continue
                            continue
                    else:
                        continue
                case 2:
                    cond=is_db_NotEmpty()
                    if cond==True:
                        while True:
                            ch=int(input("Enter\n1)To view profile\n2)To quit\n"))
                            match ch:
                                case 1:
                                    name=input("Enter name of student to view the profile\n")
                                    cond, doc_retrived=to_view_specific_student(name)
                                    if cond == True:
                                        while True:
                                            ch=int(input("Enter\n1)To view his photo\n2)To delete his profile\n3)To exit\n"))
                                            try:
                                                match ch:
                                                    case 1:
                                                        retriveImage(doc_retrived)
                                                        continue
                                                    case 2:
                                                        to_delete_a_student(name)
                                                        break
                                                    case 3:
                                                        print("Quitting...")
                                                        break
                                                    case _:
                                                        print("Invalid choice! please enter between 1 & 2.")
                                                        continue
                                            except (ValueError,NameError,EOFError):
                                                print("Admin please enter a valid choice!")
                                                continue
                                    elif cond == False:
                                        continue
                                case 2:
                                    print("Quitting...")
                                    break
                                case _:
                                    print("Invalid choice! please enter between 1 & 2.")
                                    continue
                    else:
                        continue
                case 3:
                    cond=is_db_NotEmpty()
                    if cond==True:
                        name=input("Enter the name of student you want to delete\n")
                        to_delete_a_student(name)
                        continue
                    else:
                        continue
                case 4:
                    cond=is_db_NotEmpty()
                    if cond==True:
                        to_delete_all_students()
                        continue
                    else:
                        continue
                case 5:
                    print("Admin logged out!")
                    while True:
                        try:
                            ch=int(input("Enter\n1)To stay on the app\n2)To exit the system\n"))
                            match ch:
                                case 1:
                                    return True
                                case 2:
                                    return False
                                case _:
                                    print("Invalid choice! please enter a valid between 1 & 2.")
                                    continue
                        except (ValueError, NameError, EOFError):
                            print("Invalid choice! please enter a valid choice!")
                            continue
                case _:
                    print("Invalid choice! please enter a valid choice between 1 & 2.")
                    continue

        except (ValueError,NameError,EOFError):
            print("Admin please enter a valid choice")
            continue

if __name__ == '__main__':
    Admin()