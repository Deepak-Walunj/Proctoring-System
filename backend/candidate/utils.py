from django.core.mail import send_mail
from django.conf import settings

def send_email_to_student():
    subject="This is message from eduviva server"
    message="This is test message do not replay"
    from_email = settings.EMAIL_HOST_USER
    recipient_list=["sachishinde20@gmail.com","abhijeet.22210302@vvit.ac.in"]
    send_mail(subject,message,from_email,recipient_list)