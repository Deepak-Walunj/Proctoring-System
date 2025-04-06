from django.shortcuts import render, HttpResponse 
from django.http import JsonResponse
from .db import listInterview,getQuestionSet,addCandidateToList, addFeedbackToList, fetchAllInfo,fetchListOfIndividuaLReport,saveFinalReport
from .db import addCadidatesToVivaReport,newaddFeedbackToList,addissue,getuserdetails,get_all_users,saveVideoID
# from .ml import askbot
# from mlmodel.user_input import askbot
from PIL import Image
# from mlmodel.student_verification import faceMatching
from mlmodel.chatgpt import askbot ,finalfeedback
from .auth import getuser, register_user 
from django.contrib.sessions.backends.db import SessionStore
from django.views.decorators.csrf import csrf_exempt,csrf_protect
import json
import base64
import sys
from django.core.files.storage import FileSystemStorage
from .s3 import uploadToServer
from django.conf import settings
import os
import cv2 as cv
from io import BytesIO
from tempfile import NamedTemporaryFile
from mlmodel.gcs import upload_blob


# INTERVIWEE
# Create your views here.
# route for registration
@csrf_exempt 
def register(request):
    if request.method == 'POST':
        # data = json.loads(request.body.decode('utf-8'))
        print(request.POST.get('username'))
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        gender = request.POST.get('gender')
        img=request.FILES.get('image')
        base64_string = base64.b64encode(img.read()).decode("utf-8")
        print(base64_string)

        print(username,email,password)
        data={
            "name":name,
            "username":username,
            "email":email, 
            "password":password,
            "gender":gender,
            "img":base64_string
        }

        # print(username,email,password)
        result = register_user(data)
        print(result)
        if result == "user added successfully!":
            return HttpResponse("Registration successful!")
        elif result == "user already exist":
            return HttpResponse("User already exists!")
        else:
            return HttpResponse("Registration failed!")    
    return HttpResponse("this is register route of interviewee")

# ROUTE FOR LOGIN 
@csrf_exempt 
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        username = data['username']
        password = data['password'] 
        print(username,password)
        result = getuser(username, password) 

        if result['status'] == 'Login successful':
            request.session['username']=username
            request.session.set_expiry(None)
            print(request.session['username'])
            
            return HttpResponse(f"Login successful")
        elif result['status'] == 'Invalid password':
            return HttpResponse("Invalid password!")
        elif result['status'] == 'User not found':
            return HttpResponse("User not found!")
        else:
            return HttpResponse("Login failed!")

    return HttpResponse("this is login route of interviewee")



# ROUTE TO ADD PROFILE DETAILS 
def profile(request):
    if 'username' in request.session:
        username=request.session['username']
        
        return HttpResponse(f"this is profile page of {username} ")
    return HttpResponse("i had not fount username")


# ROUTE TO UPDATE PROFILE DETAILS 
def logout(request):
    if 'username' in request.session:
        request.session.flush()
        return HttpResponse("loged out")
    return HttpResponse("i had not found username")



# LIST OF INTERVIEW (WITH OR WITHOUT FILTER ) **
def listOfInterview(request):
    res = listInterview({})
    return HttpResponse(res)


# START INTERVIEW 
def getQASet(request):
    print("requeasted for questionset")
    if request.method=='GET':
        id=request.GET.get('id')
        username=request.GET.get('username')
        # if 'username' not in request.session:
        #     return HttpResponse("Please log in first.")
        # username=request.session['username']
        entry={
            "name": username,
            "Score": 0,
            "rank": 0,
            "vivaID":id,
            "videoID":"",
            "feedback": "",
            "providedQAndA":[]
        }
        # addCandidateToList(id,entry)
        data=addCadidatesToVivaReport(entry)
        print(data)
        if data=="user added for viva":
            res,NOS_count,timer,domain=getQuestionSet(id)
            print(type(res))
            return JsonResponse({'questionset':res,'NOS_count':NOS_count,'timer':timer,'domain':domain},safe=False,content_type="application/json")
        else:
            return HttpResponse(data)
    return HttpResponse("interview not found")
# GET QUESTION
@csrf_exempt
def getquestion(request):
    if request.method=='POST':
        # data = json.loads(request.body.decode('utf-8'))
        data = request.POST.dict()
        # print(data)
        print(data.get('user_input'))
        I_id=data.get('id')
        username=data.get('username')
        questionSet=data.get('questionset')
        c_question=data.get('c_question')
        c_answer=data.get('c_answer')
        NOS_count=int(data.get('NOS_count'))
        domain=data.get('domain')
        print(NOS_count)
        # questionSet=questionSet.replace("'",'"')
        # print(username)
        audio_file=request.FILES['user_audio_file']
        print(audio_file)

        # print(questionSet)
        print(type(questionSet))
        # questionSet=ast.literal_eval(questionSet)
        questionSet = json.loads(questionSet)
        # questionSet=list(questionSet)
        q_history=data.get('q_history') 
        q_history=json.loads(q_history)
        # print(q_history)
        print(type(q_history))
        # print()


        if username and questionSet:

            user_input=data.get('user_input')

            if(user_input=='start'):
                output=askbot(user_input,"audio_file",questionSet,"","",q_history,NOS_count,domain)
                print(output)
                return JsonResponse({"question":output['question'],"answer":output['answer'],'NOS':output['NOS']})
                # return HttpResponse(output['question'] + output['answer'])
            elif(user_input=='end'):
                return HttpResponse("thank you")
            else:
                temp_dir = settings.BASE_DIR / "temp"
                os.makedirs(temp_dir, exist_ok=True)
                try:
                    with NamedTemporaryFile(delete=False, suffix=".wav", dir=temp_dir) as temp_file:
                        for chunk in audio_file.chunks():
                            temp_file.write(chunk)
                        temp_file_path = temp_file.name

                except Exception as e:
                    print(f"Error saving temporary file: {e}")
                    return JsonResponse({"error": "File saving failed"}, status=500)        

                print(temp_file_path)
                name=f"{I_id}_{username}_{len(q_history)}.wav"
                print(name)
                uri=upload_blob(temp_file_path,name)

                output=askbot(user_input,uri,questionSet,c_question,c_answer,q_history,NOS_count,domain)
                # print(output['data']['Scorer'])
            #     data={
            #         "question": c_question,
            #         "userans":user_input,
            #         "answer_checker":str(output['data']['answer_checker'].raw),
            #         "responder":str(output['data']['responder'].raw),
            #         "feedback_provider":str(output['data']['feedback_provider'].raw),
            #         "Scorer":str(output['data']['Scorer'].raw),
            #         "performance_report":str(output['data']['performance_report'].raw),
                
            # }
                data1={
                    "question": c_question,
                    "userans":output['data']['transcribed text'],
                    "Analysis":output['data']
                    # "score":output['data']['human_evaluation']['Total Average Score'],
                    # "summary":output['data']['human_evaluation'],
                    # "feedback":output['data']['Overall Feedback'],
                    # "speech_analysis":output['data']['Speech_analysis']

                }
                # print( "data is" ,data)
                # res=addFeedbackToList(I_id,username,data)
                res=newaddFeedbackToList(I_id,username,data1)
                print(res)
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            
                # function
                print(".............................................................")
                print("new question is : ", output['question'])
                print(".............................................................")
                print("answer of that question is ",output['answer'])
                print(".............................................................")
                # request.session['c_question']=str(output['question'].raw)
                # request.session['q_history'].append(str(output['question'].raw))
                # request.session['c_answer']=str(output['answer'].raw)
                return JsonResponse({"question":output['question'],"answer":output['answer'],'NOS':output['NOS']})
                
                # return HttpResponse(str(output['question'].raw) + str(output['answer'].raw))
        else:
            return HttpResponse("plz login first no data is found")
        
# final report 
def generatefinalreport(request):
    I_id=request.GET.get("id")
    username=request.GET.get("username")
    lt=fetchListOfIndividuaLReport(I_id,username)
    report=finalfeedback(lt)
    # print(report)
    if report:
        res=saveFinalReport(I_id,username,report)
        return HttpResponse(res)
    else:
        return HttpResponse("error in report generating")
    

@csrf_exempt
def report_issue(request):
    if request.method=='POST':
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        doc={
            'name':data.get('name'),
            'issue':data.get('issue'),
            'date_time':data.get('date'),
        }
        res=addissue(doc)
        if res=='error':
            return HttpResponse("Error please try again")
        return HttpResponse('Thank you '+data.get('name')+ ". Your issue has been submitted successfully!")





# END AND SHOW SCORE  
def showScore(request):
    I_id=request.GET.get("id")
    username=request.GET.get("username")
    print("Request for final feedback")
    if username and I_id:
        response=fetchAllInfo(I_id,username)
        print(type(response))
        return JsonResponse(response[0])
        

# LEADERBOARD FOR SPEACIFIC INTERVIEW  

# NOTIFICATION OF PASSED OR FAILED 



# PERSONAL DASHBOARD z

def getUserData(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        if not username:
            return JsonResponse({"error": "Username is required"}, status=400)
        
        try:
            user_data = getuserdetails(username)
            print("user_data : ",user_data)
            if user_data:
                return JsonResponse(user_data, status=200)
            else:
                return JsonResponse({"error": "User not found"}, status=404)
        except Exception as e:
            print("error: ",e)  # Log the error for debugging
            return JsonResponse({"error": "Internal server error"}, status=500)

    return JsonResponse({"error": "Invalid request method. Only GET allowed."}, status=405)


def get_all_users_view(request):
    if request.method == 'GET':
        try:
            # Fetch all users using the helper function
            users = get_all_users()
            
            if users:
                # Return the data as a JSON response
                return JsonResponse({"users": users}, safe=False, status=200)
            else:
                # If no users are found
                return JsonResponse({"error": "No users found"}, status=404)
        except Exception as e:
            # Log any unexpected errors and return a server error response
            print(f"Error in get_all_users_view: {e}")
            return JsonResponse({"error": "Internal server error"}, status=500)

    # Return a method not allowed response for non-GET requests
    return JsonResponse({"error": "Invalid request method. Only GET allowed."}, status=405) 

@csrf_exempt
def upload_video(request):
    if request.method == 'POST' and 'video' in request.FILES:
        video_file = request.FILES['video']
        video_content = video_file.read()
        username=request.POST.get('username')
        vivaID=request.POST.get('vivaID')
        print(vivaID,username)


        # Base64 encode the video content
        # encoded_video = base64.b64encode(video_content).decode('utf-8')
        # print(sys.getsizeof(encoded_video))
        file_key = f"{vivaID}_{username}.mp4"
        print(file_key)
        temp_dir = settings.BASE_DIR / "temp"
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # Save the video file temporarily
            with NamedTemporaryFile(delete=False, suffix=".mp4", dir=temp_dir) as temp_file:
                for chunk in video_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            # Upload to S3 using the file path
            try:
                videolink=uploadToServer(temp_file_path,file_key)

                # Save video link in the database
                res = saveVideoID(vivaID, username, videolink)

                if res != "error":
                    return JsonResponse({"res": "video completed"}, status=200)
                else:
                    return JsonResponse({"error": "Database error"}, status=500)
            except Exception as e:
                print(f"Error uploading to S3: {e}")
                return JsonResponse({"error": "S3 upload failed"}, status=500)
            finally:
                # Delete the temporary file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        except Exception as e:
            print(f"Error saving temporary file: {e}")
            return JsonResponse({"error": "File saving failed"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
        
        
        
        
        
@csrf_exempt
def upload_audio(request):
    if request.method == 'POST':
        # Check if the request contains the 'audioFile'
        if 'audioFile' in request.FILES:
            audio_file = request.FILES['audioFile']
            
            # Optionally, save the file to the server (e.g., under a specific directory)
            # fs = FileSystemStorage()
            # filename = fs.save(audio_file.name, audio_file)  # Save to the server
            # file_url = fs.url(filename)  # Get the URL for the uploaded file
            # 
            # Return success response
            return JsonResponse({"res": "audio recorded"}, status=200)
        
        return JsonResponse({"error": "No file uploaded"}, status=400)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)


def decode_base64_image(base64_string):
    try:
        base64_string = base64_string.split(",")[1]  # Remove data:image/png;base64, part
        decoded_image = base64.b64decode(base64_string)
        return Image.open(BytesIO(decoded_image))
    except Exception as e:
        print("Error decoding base64:", e)
        return None


def decode_base64_imagefromdb(base64_str):
    """Decodes Base64URL to binary image data safely."""
    try:
        base64_str = base64_str.replace("-", "+").replace("_", "/")  # Convert Base64URL to Base64
        return base64.b64decode(base64_str)
    
    except Exception as e:
        print("Error decoding Base64 image:", e)
        return None 


@csrf_exempt
def verifyface(request):
    if request.method == 'POST':
        print("requested for face verification")
        # data = json.loads(request.body.decode('utf-8'))
        # print(len(data))
        # if(data["vivaImg"]):
        #     print("vivaimg")
        # if(data["username"]):
        #     print("username")
        username=request.POST.get('username')
        user_data = getuserdetails(username)

        vivaImg=request.FILES['vivaImg']
        base64_string = base64.b64encode(vivaImg.read()).decode("utf-8")

        vivaImg=decode_base64_imagefromdb(base64_string)
        pil_vivaIMG=Image.open(BytesIO(vivaImg))
        if(pil_vivaIMG):
            print(type(pil_vivaIMG))
        # vivaImg=decode_base64_imagefromdb(data["vivaImg"])
        # with open("viva_image.png", "wb") as img_file:
        #     img_file.write(vivaImg)
        # vivaImg = base64.b64decode(vivaImg)

        #         # Create an image from the decoded bytes
        # vivaImg = Image.open(BytesIO(vivaImg))

        # profileImg=request.FILES['profileImg']
        profileImg=decode_base64_imagefromdb(user_data['img'])
        pil_profileIMG=Image.open(BytesIO(profileImg))
        # with open("profile_image.png", "wb") as img_file:
        #     img_file.write(profileImg)
        # profileImg = base64.b64decode(profileImg)
        #         # Create an image from the decoded bytes
        # profileImg = Image.open(BytesIO(profileImg))
        print(type(pil_profileIMG))
        
        if vivaImg and profileImg:
            print("both img are collected")
        try:
            # output ,result , toast=faceMatching(pil_profileIMG,pil_vivaIMG)
            print("output")
            # if output['verified']:
                # print("face matched")
                # return JsonResponse({"res": "face verified"}, status=200)
            # return  JsonResponse()
            # else:
            #     print("not matched")
            #     return JsonResponse({"res": "face not verified"}, status=401)
        except Exception as e:
            print("error while verification: ",e)
            return JsonResponse({"error": e}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)
    