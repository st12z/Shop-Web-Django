import smtplib
import ssl
from django.core.mail import EmailMessage
from helper.generateOtp import generateOtp
from django.conf import settings
import socket
socket.getaddrinfo('localhost', 8080)
def send_reset_email(email):
    # Tạo mã OTP
    token = generateOtp(6)
    
    # Thông tin email
    subject = "Mã OTP"
    message = f"Mã OTP của bạn: {token}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    try:
        # Tạo một SSLContext không xác minh chứng chỉ
        context = ssl._create_unverified_context()
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            email_message = EmailMessage(subject, message, email_from, recipient_list)
            email_message.send(fail_silently=False)
        print("Email đã được gửi thành công!")
    except Exception as e:
        print(f"Có lỗi xảy ra khi gửi email: {e}")
