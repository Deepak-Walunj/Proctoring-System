import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from detection_classes.centralisedDatabaseOps import DatabaseOps

def Admin():
    print("*"*50,"Welcome Admin","*"*50)
    dbOps=DatabaseOps()
    while True:
        try:
            ch=int(input("Enter\n1)To view all documents\n2)To view a student\n3)To delete a student\n4)To delete all students\n5)To logout\n"))
            match ch:
                case 1:
                    cond, toast=dbOps.is_db_NotEmpty()
                    print(toast)
                    if cond==True:
                        status, all_docs, toast=dbOps.to_view_all_students()
                        if status==False:
                            print(toast)
                            continue
                        else:
                            print(toast)
                            for docs in all_docs:
                                print(docs)
                        while True:
                            try:
                                to_del=int(input("Enter:\n1)To delete all records form the database!\n2)Quit\n"))
                                match to_del:
                                    case 1:
                                        status, toast=dbOps.to_delete_all_students()
                                        print(toast)
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
                    cond, toast=dbOps.is_db_NotEmpty()
                    print(toast)
                    if cond==True:
                        while True:
                            ch=int(input("Enter\n1)To view profile\n2)To quit\n"))
                            match ch:
                                case 1:
                                    name=input("Enter name of student to view the profile\n")
                                    cond, doc_retrived, toast=dbOps.to_view_specific_student(name)
                                    print(toast)
                                    if cond == True:
                                        while True:
                                            ch=int(input("Enter\n1)To view his photo\n2)To delete his profile\n3)To exit\n"))
                                            try:
                                                match ch:
                                                    case 1:
                                                        pil_image, dbIstatus, dbItoast=dbOps.take_photo_from_database(name)
                                                        if dbIstatus:
                                                            pil_image.show()
                                                        else:
                                                            print(dbItoast)
                                                        continue
                                                    case 2:
                                                        status, toast=dbOps.to_delete_a_student(name)
                                                        print(toast)
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
                    cond, toast=dbOps.is_db_NotEmpty()
                    print(toast)
                    if cond==True:
                        name=input("Enter the name of student you want to delete\n")
                        status, toast=dbOps.to_delete_a_student(name)
                        print(toast)
                        continue
                    else:
                        continue
                case 4:
                    cond, toast=dbOps.is_db_NotEmpty()
                    print(toast)
                    if cond==True:
                        status, toast=dbOps.to_delete_all_students()
                        print(toast)
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