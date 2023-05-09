from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.apps import apps
#resetpassword generators and modules
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import NoReverseMatch, reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.core.mail import BadHeaderError, send_mail
from django.core import mail
from .utils import TokenGenerator, generate_token
from django.conf import settings

Account = apps.get_model('accounts', 'Account')

# Create your views here.



#Threading
import threading

class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        super().__init__()
    def run(self):
        self.email_message.send()
        threading.Thread.__init__(self)



#Reset Password
class RequestResetEmailView(View):
    def get(self, request):
        return render(request, 'registrations_temp/request-reset-email.html')
    
    def post(self, request):
        email = request.POST['email']
        user = Account.objects.filter(email=email)

        if user.exists():
            current_site    = get_current_site(request)
            email_subject   = '[Reset Your Password]'
            message         = render_to_string('registrations_temp/reset-user-password.html',
            {
                'domain': '127.0.0.1:8000',
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
            })

            email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
            EmailThread(email_message).start()

            messages.info(request, "We have sent you an email with instructions on how to reset the password")
            return render(request, 'accounts_temp/login.html')
        


#Set New Password
class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.warning(request, "Password Reset Link is Invalid")
                return render(request, 'registrations_temp/request-reset-email.html')
            
        except DjangoUnicodeDecodeError as identifier:
            pass

        return render(request, 'registrations_temp/set-new-password.html', context)
    
    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }

        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password != confirm_password:
            messages.warning(request, "Password is Not Matching")
            return render(request, 'registrations_temp/set-new-password.html', context)
        
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password Reset Success. Please login with New Password')
            return redirect('login_user')
        
        except DjangoUnicodeDecodeError as identifier:
            messages.error(request, 'Something went wrong')
            return render(request, 'registrations_temp/set-new-password.html', context)