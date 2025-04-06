from django.core.mail import send_mail
from django.conf import settings

def send_email_to_student():
    subject="This is message from eduviva server"
    message="This is test message do not replay"
    from_email = settings.EMAIL_HOST_USER
    recipient_list=["sachishinde20@gmail.com","abhijeet.22210302@viit.ac.in","sneha.22210052@viit.ac.in","jay.22211405@viit.ac.in","deepak.22211041@viit.ac.in","prathmesh.22211184@viit.ac.in","sarvesh.22210159@viit.ac.in","dhanraj.22210367@viit.ac.in"]
    send_mail(subject,message,from_email,recipient_list)