from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, first_name, phone, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, first_name, phone, password, **other_fields)

    def create_user(self, email, first_name, phone, password, **other_fields):
        other_fields.setdefault('is_active', True)
        
        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, phone=phone, **other_fields)
        user.set_password(password)
        user.save()
        return user


class NewUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(_('mobile number'), max_length=20, unique=True)
    start_date = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'phone']

    def __str__(self):
        return self.first_name


#Account Balance
class AccountBalance(models.Model):
    User = models.OneToOneField(NewUser, on_delete=models.CASCADE, related_name='balance')
    Date = models.DateTimeField(auto_now=True)
    Available_Balance = models.DecimalField(decimal_places=2, max_digits=10, default=2000)


    def __str__(self):
        return self.User.email
    
#Transfer/Transaction
class Transfer(models.Model):
    User = models.ForeignKey(NewUser, on_delete=models.CASCADE, related_name='transfers')
    Date = models.DateTimeField(auto_now_add=True)
    Amount = models.DecimalField(decimal_places=2, max_digits=10, blank=False)
    Discription = models.CharField( max_length=50)
    Destination = models.CharField( max_length=20)

    def __str__(self):
        return self.Amount and self.Destination

class Deposit(models.Model):
    User = models.ForeignKey(NewUser, on_delete=models.CASCADE, related_name='deposits')
    Date = models.DateTimeField(auto_now_add=True)
    Amount = models.DecimalField(decimal_places=2, max_digits=10, blank=False)

    def __str__(self):
        return self.User.email



