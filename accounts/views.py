from django.contrib import messages,auth,sessions
from django.shortcuts import render,redirect
from .forms import Registrationform
from .models import Account
from django.contrib.auth.decorators import login_required

# vertification email and reset password
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.views.decorators.cache import cache_control
import re, random
from datetime import datetime, timedelta
from django.utils import timezone


from twilio.base.exceptions import TwilioRestException
from django.conf import settings
from twilio.rest import Client


OTP_EXPIRY_MINUTES = 5


# Create your views here.



#SignUp
# @cache_control(no_cache=True, must_revalidate =True, no_store=True)
def sign_up(request):
    if 'email' in request.session:
        return redirect('home')
    
    if request.method=='POST':
        form = Registrationform(request.POST)
        if 'email-otp' in request.POST:
            if form.is_valid():
                email = form.cleaned_data['email']
                username = form.cleaned_data['username']
                phone = form.cleaned_data['phone']
                password = form.cleaned_data['password']
                confirm_password = form.cleaned_data['confirm_password']

                #generating OTP and Sending Email
                otp_no = str(random.randint(100000, 999999))
                message = f"""Hi {username},

    Thank you for registering with Razopy.

    Please use the following OTP code to verify your email id: {otp_no}
    """
                email_subject = "Verify your email address"
                email_to = form.cleaned_data['email']
                email = EmailMessage(email_subject, message, to=[email_to])
                email.send()

                # Store OTP in session
                request.session['username'] = username
                request.session['phone'] = phone
                request.session['email'] = email_to
                request.session['password'] = password
                request.session['otp'] = otp_no
                request.session['otp_timestamp'] = datetime.now().isoformat()
                
                return render(request, 'accounts_temp/otp.html', {'email': email_to})
            else:
                messages.info(request, 'Both passwords are not matching')
                return redirect('sign_up')
            

        if 'sms-otp' in request.POST:
            if form.is_valid():
                email = form.cleaned_data.get('email')
                username = form.cleaned_data.get('username')
                phone = form.cleaned_data.get('phone')
                password = form.cleaned_data.get('password')

                # Generate OTP
                otp = generate_otp()

                # Send OTP to user's phone number
                send_otp(otp, phone)

                # Store user data and OTP in session
                request.session['email'] = email
                request.session['username'] = username
                request.session['phone'] = phone
                request.session['password'] = password
                request.session['otp'] = otp

                return redirect('otp_verification')
    else:
        form=Registrationform()
    context = {
        'form': form,
    }
    return render(request, 'accounts_temp/sign-up.html', context)



#Genarating OTP
def generate_otp():
    import random
    return str(random.randint(100000, 999999))



#Sending OTP
def send_otp(otp, phone):
    client = Client('AC533d11df9be75ebc56c5b24db413f828', 'fd54d9c138eac633edeb07231f22b079')
    message = client.messages.create(
        body=f'Your OTP is {otp}.',
        from_='+15677042685',
        to=phone
    )
    print(message.sid)


#Email OTP verification function
def otp_func(request):
    if request.method == 'POST':
        email = request.POST['email']
        otp = request.POST['otp']

        
        #OTP verification
        if 'otp' in request.session and 'otp_timestamp' in request.session:
            otp_timestamp = timezone.make_aware(datetime.fromisoformat(request.session['otp_timestamp']))
            now = timezone.now()
            email = request.session['email']
            if request.session['otp'] == otp and otp_timestamp >= now - timedelta(minutes=OTP_EXPIRY_MINUTES):

                #Get username and password 
                username = request.session.get('username')
                phone = request.session.get('phone')
                password = request.session.get('password')

                # Create user
                user = Account.objects.create_user(email=email, username=username, phone=phone, password=password)
                user.phone=phone
                user.set_password(password)
                user.is_active = True
                user.save()

                # Clear OTP
                del request.session['otp']
                del request.session['otp_timestamp']
                del request.session['username']
                del request.session['phone']
                del request.session['email']
                del request.session['password']

                messages.success(request, 'Account created successfully!')
                return redirect('login_user')
            else:
                messages.info(request, 'Invalid OTP or OTP has expired.')
                return redirect('otp_func')
    else:
        email = request.GET.get('email')
        if email is None:
            return redirect('sign_up')
        else:
            return render(request, 'accounts_temp/otp.html', {'email': email})



#SMS OTP verificaton
def otp_verification(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        phone = request.session.get('phone')

        if otp == request.session.get('otp'):
            # Create user
            email = request.session.get('email')
            username = request.session.get('username')
            phone = request.session.get('phone')
            password = request.session.get('password')
            user = Account.objects.create_user(email=email, username=username, phone=phone, password=password)
            user.is_active = True
            user.save()

            # Clear session data
            del request.session['email']
            del request.session['username']
            del request.session['phone']
            del request.session['password']
            del request.session['otp']

            messages.success(request, 'Account created successfully. Please login.')
            return redirect('login_user')
        else:
            messages.error(request, 'Some problem with OTP verification')
            return redirect('otp_verification')
            # messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'accounts_temp/otp_verification.html')
        


#Login
# @cache_control(no_cache=True, must_revalidate =True, no_store=True)
def login_user(request):
    if 'email' in request.session:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user=auth.authenticate(email=email,password=password)
        if user is not None:
            request.session['email'] = email
            auth.login(request,user)
            return redirect('home')

        else:
            messages.error(request,'Invalid login credentials')
            return redirect('login_user')
    return render(request, 'accounts_temp/login.html')



#Logout
@login_required(login_url='login_user')
def logout_user(request):
    auth.logout(request)
    return redirect('home')