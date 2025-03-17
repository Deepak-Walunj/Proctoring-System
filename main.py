from registration.register import register
from login.login import login
from admin.admin import Admin
from student_verification.student_verification import studentVerification
from starting_viva.liveProctoring import liveProctoring
cond1=False
def main():
    print("*"*50,"Welcome!","*"*50)
    while True:
        try:
            ch=int(input("Enter:\n1)For Registeration\n2)For login\n3)For admin login\n4)For student verification\n5)To start the test\n6)To exit\n"))
            match ch:
                case 1:
                    print("\n","*"*50,"Welcome to registeration","*"*50)
                    name=input("Enter your name:\n")
                    doc_id=register(name)
                    if doc_id is not None:
                        print(f"Student {name} register with id:{doc_id}")
                        exit()
                    else:
                        continue
                case 2:
                    print("\n","*"*50,"Welcome to login","*"*50)
                    name=input("Enter your name:\n")
                    cond1, retrived_doc=login(name)
                    if cond1:
                        print("\n","*"*50,'Successfully logged into to the Test Dashboard!',"*"*50)
                        print("For giving test you will first go throught student verification!\n")
                    else:
                        print("Some credentials are wrong!")
                    break
                case 3:
                    print("\n","*"*50,"Welcome to login","*"*50)
                    cond=Admin()
                    if cond==True:
                        continue
                    elif cond==False:
                        break
                case 4:
                    print("You are about to give test.\nBefore giving the test you will go through student verfication process..")
                    result, verifStatus, verifToast=studentVerification(name)
                    if verifStatus==True:
                        print(f"{verifToast}")
                        print(result.get("verified"))
                        print("User Verified!\nGet ready for the viva...")
                    else:
                        print(f"Not able to verify student: {verifToast}")
                case 5:
                    print("We are starting our exam.....")
                    name=input("Please enter your name! ")
                    pStatus, pToast, gazeResult, objectDetectionResult, gaze_toast, objectDetectionToast=liveProctoring(name)
                    if pStatus==True:
                        print(f"Proctoring ended with status: {pStatus} and toast: {pToast}")
                        print(f"Gaze Toast: {gaze_toast} and result: {gazeResult}")
                        print(f"Object Detection Toast: {objectDetectionToast} and result: {objectDetectionResult}")
                        break
                    else:
                        print("Proctoring failed")
                case 6:
                    print("Exiting...")
                    exit()
                case _:
                    print("Invalid Choice!\nPlease chose between 1 & 2.")
                    continue
        except Exception as e:
            print(f"[Error] in main :{e}")
            continue
if __name__ == '__main__':
    main()