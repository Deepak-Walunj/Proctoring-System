
from django.urls import path
from company import views

urlpatterns = [
    path("createinterview",views.createinterview,name='createinterview'),
    # path("createAiinterview",views.createAiinterview,name='createAiinterview'),
    # path("generateQuestion",views.generateQuestion,name='generateQuestion'),
    path("showVivas",views.showVivas,name='showVivas'),
    path("updatetimer",views.updatetimer,name='updatetimer'),
    path("candidates",views.getlistofcandidate,name='getlistofcandidate'),
    path("updateQuestionSet",views.updateQuestionSet,name='updateQuestionSet'),
    path("deleteVIVA",views.deleteVIVA,name='deleteVIVA'),
    path("getlistofcandidate",views.getlistofcandidate,name='getlistofcandidate'),
    path("seeindividualfeedback",views.seeindividualfeedback,name='seeindividualfeedback'),
    path("send_mail_to_candidates",views.send_mail_to_candidates,name='send_mail_to_candidates'),
    path("getIssue",views.getIssues,name='getIssue'),
    path("updateStatus",views.updateStatus_view,name='updateStatus'),
    
]
