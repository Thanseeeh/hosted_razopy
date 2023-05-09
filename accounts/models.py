from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from users.models import Wallet

# Create your models here.


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, phone, password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have an username')
        if not phone:
            raise ValueError('User must have a phone number')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            phone = phone,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, phone, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            phone = phone,
            password = password,
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user
    


class Account(AbstractBaseUser):
    email       = models.EmailField(max_length=100, unique=True)
    username    = models.CharField(max_length=100, unique=True)
    phone       = models.CharField(max_length=20)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login  = models.DateTimeField(auto_now_add=True)
    is_admin    = models.BooleanField(default=False)
    is_staff    = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to='profiles', default='profile.png', null=True, blank=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    objects = MyAccountManager()

    def str(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True
    
    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        if created:
            Wallet.objects.create(user=self)