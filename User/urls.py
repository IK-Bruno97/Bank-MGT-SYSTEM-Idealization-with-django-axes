from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
urlpatterns = [
    path('signup/', RegisterPage.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('login/', Login.as_view(), name='login'),
    path('details/', AccountDetailsView.as_view(), name='details'), 
    path('deposit/', DepositView.as_view(), name='deposit'), 
    path('logout/',LogoutView.as_view(next_page='login', extra_context={'message':'Logged Out. Thank you for banking with us.'}), name='logout'), 
    path('set-new-password/<uidb64>/<token>', SetNewPasswordView.as_view(), name='set-new-password'),
    path('request-reset-email', RequestResetEmailView.as_view(), name='request-reset-email')
]

