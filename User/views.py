from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib.auth import login 
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site

from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View

from django.conf import settings
from .forms import SignUpForm
from django.urls import reverse_lazy
from .models import NewUser, Transfer, AccountBalance, Deposit

from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from validate_email import validate_email
import threading


# Create your views here.
class Login(LoginView):
    template_name = 'users/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('details')
            
"""
class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.add_message(request, messages.SUCCESS, "Logged Out. Thank you for banking with us.")
        return redirect('login')
"""


class RegisterPage(FormView):
    template_name = 'users/register.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('login')
        return super(RegisterPage, self).get(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('users/activate.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': force_str(urlsafe_base64_encode(force_bytes(user.pk))),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
            
        return super(RegisterPage, self).form_valid(form)



def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = NewUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, NewUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        bal = AccountBalance.objects.create(User=user, Available_Balance="2000")
        bal.save()
    
        login(request, user)
        return redirect('details')
        #return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')




class AccountDetailsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {
            'Transfers' : Transfer.objects.all().filter(User=request.user).order_by('-Date'),
            'Deposits' : Deposit.objects.all().filter(User=request.user).order_by('-Date'),
        }
        return render(request, 'users/acctview.html', context)

    def post(self, request):
        user = self.request.user 

        #get the submited data from Transfer form
        amount = request.POST.get('amount')
        destination = request.POST.get('destination')
        discription = request.POST.get('discription')
        #get user acct bal
        debitor = AccountBalance.objects.get(User=user) #Transfer


       #verify if acct number/ph_number from Destination field exists in Db for Transfer Success
        if NewUser.objects.get(phone=destination):
            if int(amount) < debitor.Available_Balance:
                Transaction = Transfer.objects.create(
                        User=user,
                        Amount=amount,
                        Destination=destination,
                        Discription=discription,
                )
                #deduct the amount from user acct balance
                debitor.Available_Balance -= int(amount)
                debitor.save()

                #add the amount to beneficiary acct balance
                beneficiary = NewUser.objects.get(phone=destination)
                credit = AccountBalance.objects.get(User=beneficiary)
                credit.Available_Balance += int(amount)
                credit.save()
                
                Transaction.save()
                return render(request, 'users/success.html')

        else:
            return HttpResponse('Invalid account number!')
       
class DepositView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'users/deposits.html')

    def post(self, request):
        user = self.request.user 

        #get the submited data from Deposit form
        deposit = request.POST.get('deposit')

        creditor = AccountBalance.objects.get(User=user) 
        
        #Make actual deposit into user account
        Deposited = Deposit.objects.create(
                        User=user, 
                        Amount=deposit,
        )
        creditor.Available_Balance += int(deposit)
        Deposited.save()
        creditor.save()

        return render(request, 'users/success.html')



class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()

class RequestResetEmailView(View):
    def get(self, request):
        return render(request, 'users/request-reset-email.html')

    def post(self, request):
        email = request.POST['email']

        if not validate_email(email):
            messages.error(request, 'Please enter a valid email')
            return render(request, 'users/request-reset-email.html')

        user = NewUser.objects.filter(email=email)

        if user.exists():
            current_site = get_current_site(request)
            email_subject = '[Reset your Password]'
            message = render_to_string('users/reset-user-password.html',
                                       {
                                           'domain': current_site.domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                                           'token': PasswordResetTokenGenerator().make_token(user[0])
                                       }
                                       )

            email_message = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [email]
            )

            EmailThread(email_message).start()

        messages.success(
            request, 'We have sent you an email with instructions on how to reset your password')
        return render(request, 'users/request-reset-email.html')




class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))

            user = NewUser.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(
                    request, 'Password reset link, is invalid, please request a new one')
                return render(request, 'users/request-reset-email.html')

        except DjangoUnicodeDecodeError as identifier:
            messages.success(
                request, 'Invalid link')
            return render(request, 'users/request-reset-email.html')

        return render(request, 'users/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
            'has_error': False
        }

        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if len(password) < 6:
            messages.add_message(request, messages.ERROR,
                                 'passwords should be at least 6 characters long')
            context['has_error'] = True
        if password != password2:
            messages.add_message(request, messages.ERROR,
                                 'passwords don`t match')
            context['has_error'] = True

        if context['has_error'] == True:
            return render(request, 'users/set-new-password.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))

            user = NewUser.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(
                request, 'Password reset success, you can login with new password')

            return redirect('login')

        except DjangoUnicodeDecodeError as identifier:
            messages.error(request, 'Something went wrong')
            return render(request, 'users/set-new-password.html', context)

        return render(request, 'auth/set-new-password.html', context)
