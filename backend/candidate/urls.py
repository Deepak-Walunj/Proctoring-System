
from django.contrib import admin
from django.urls import path
from candidate import views


urlpatterns = [
    path("login",views.login,name='login'),
    path("register",views.register,name='register'),
    path("profile",views.profile,name='profile'),
    path("listOfInterview",views.listOfInterview,name='listOfInterview'), 
    path("logout",views.logout,name='logout'),
    path("getquestion",views.getquestion,name='getquestion'),
    path("getQASet",views.getQASet,name='getQASet'),
    path("showScore",views.showScore,name='showScore'),
    path("generatefinalreport",views.generatefinalreport,name='generatefinalreport'),
    path('report_issue', views.report_issue, name='report_issue'),
    path('getUserData', views.getUserData, name='getUserData'),
    path('getAllUsers', views.get_all_users_view, name='getAllUsers'),
    path('upload_video/',views.upload_video,name='upload_video/'),
    path('upload_audio/',views.upload_audio,name='upload_audio/'),
    path('verifyface',views.verifyface,name="verifyface"),
    
]

