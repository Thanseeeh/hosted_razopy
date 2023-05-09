from django.urls import path, include
from . import views


urlpatterns = [
    path('logout_user/', views.logout_user, name='logout_user'),
    path('login_user/', views.login_user, name='login_user'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('otp-func/', views.otp_func, name='otp_func'),
    path('otp_verification/', views.otp_verification, name='otp_verification'),
]