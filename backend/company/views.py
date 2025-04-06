from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
import json
from .db import createInterview,listInterview,convert_objectid_to_string,updateTimer,getListFromInterview,updateSetOfQuestions,deleteviva,getIndividualData,getIssuesData,updateStatus
import openpyxl
from .excel_to_json import exceltolist
# from mlmodel.gpt_questions import getJsonformattedQuestionAnswerSet
from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.csrf import ensure_csrf_cookie
from .encp import generate_unique_VIVA_id
from .utils import send_email_to_student
from .db import check_duplicate_viva





# Interviewer
#Create your views here

#Add interview
@csrf_exempt  
def createinterview(request):
    print("route found")
    if request.method=='POST':
        print("requested")
        company_name = request.POST.get('companyName')
        print(company_name)
        interview_domain = request.POST.get('interviewDomain')
        print(interview_domain)
        timeforthinking=request.POST.get('timeforthinking')
        print(timeforthinking)
        status=request.POST.get('status')
        print(status)
        excelfile = request.FILES.get('excelFile') 
        print(excelfile)
        if check_duplicate_viva(company_name, interview_domain):
            return HttpResponse(
                "An interview with the same Viva Name and domain already exists."
            )
        questionset=[]
        if(excelfile):
            print("yes there is a excel file")
            questionset ,nos_count= exceltolist(excelfile)
            if(nos_count==0):
                return HttpResponse("error: row with empty nos found")

            print(questionset)
            print(type(questionset))

        if isinstance(questionset, str):
            questionset = json.loads(questionset)
        elif isinstance(questionset, list):
            # If it's already a list, skip the json.loads step
            print("Questionset is already a list, no need for json.loads")  
            
        arr = {
            "nameofviva":company_name,
            "domain": interview_domain,
            "vivaID":generate_unique_VIVA_id(),
            "timeforthinking":int(timeforthinking),
            "status":status,
            "NOS_count":int(nos_count),
            "questionSet":questionset,
            "list":[]
            }
        try:
            # print(arr)
            res = createInterview(arr)
            print(res)
            return HttpResponse(arr)
        except Exception as e:
            print("error in views: " ,e)
            return HttpResponse("error")

def send_mail_to_candidates(request):
    send_email_to_student()
    print("mail is sent")
    return HttpResponse("mail is sent")
    

def showVivas(request):
    print("request is collected at show viva route")
    lt=listInterview({})
    converted_data = convert_objectid_to_string(lt)
    print(type(converted_data))
    return JsonResponse(converted_data,safe=False)

def  updatetimer(request):
    print("reqested for updatetimer")
    vivaID=request.GET.get("vivaID")
    newtime=request.GET.get("newtime")
    res=updateTimer(vivaID,int(newtime))
    print(res)
    if res:
        return HttpResponse("updated")
    else:
        return HttpResponse("something went wrong")

def updateStatus_view(request):
    print("on update status route")
    vivaID=request.GET.get("vivaID")
    status=request.GET.get("status")
    res=updateStatus(vivaID,status)
    return HttpResponse("status updated")


#List of candidate who had given interview
def getlistofcandidate(request):
    vivaID=request.GET.get("vivaID")
    print("get list of candidate route")
    data=getListFromInterview(vivaID)
    print(data)
    return JsonResponse(data,safe=False)
    
# update questionset
def updateQuestionSet(request):
    vivaID=request.GET.get("vivaID")
    questionSet=request.GET.get("questionSet")
    questionSet=json.loads(questionSet)
    res=updateSetOfQuestions(vivaID,questionSet)
    print(res)
    if res:
        return JsonResponse({"status":"updated"},safe=False)
    else:
        return JsonResponse({"status":"not updated"},safe=False)


def seeindividualfeedback(request):
    vivaID=request.GET.get("vivaID")
    name=request.GET.get("name")
    res=getIndividualData(vivaID,name)
    return JsonResponse(res,safe=False)


#Select candidate based on score



#Interview must be deleted after time limit
def deleteVIVA(request):
    print("on delete viva route")
    vivaID=request.GET.get("vivaID")
    res=deleteviva(vivaID)
    print(res)
    if res:
        return JsonResponse({"status":"deleted"},safe=False)
    else:
        return JsonResponse({"status":"not deleted"},safe=False)

def getIssues(request):
    print("on get issues route")
    res = getIssuesData()  # Call the corrected function to fetch the issues
    print(res)
    return JsonResponse(res, safe=False)

# def getVideo(request):
#     videoID=request.GET.get('videoID')
#     print(videoID)
#     vivaFILE=getMP4(videoID)
#     if not vivaFILE:
#         return HttpResponse("Error: Video not found or failed to load.", status=404)
#     return vivaFILE


#Send mail to candidate who are selected

