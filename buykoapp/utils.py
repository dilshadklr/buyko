from django.core.mail import send_mail
import random

def send_email_otp(email):
    otp = random.randint(100000, 999999)

    subject = "Your Login OTP"
    message = f"Your OTP is {otp}. Do not share it with anyone."

    send_mail(
        subject,
        message,
        "dilshadklr04@gmail.com",
        [email],
        fail_silently=False,
    )

    return otp
