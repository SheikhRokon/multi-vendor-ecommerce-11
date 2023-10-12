from email.policy import default
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

# phone_validator = RegexValidator(r"^(\+?\d{0,4})?\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{4}\)?)?$", "The phone number provided is invalid")


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = None
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    

class Profile(models.Model):
    user                = models.OneToOneField(User, on_delete=models.CASCADE, max_length=1)
    image               = models.ImageField(upload_to="profilepicture", default='no_img.png')
    date_of_birthday    = models.DateField(auto_now_add=False,blank=True,null=True)
    phone               = models.CharField(max_length=15,unique=True,blank=True,null=True)
    permanent_address   = models.CharField(max_length=100,blank=True,null=True)
    present_address     = models.CharField(max_length=100,blank=True,null=True)


    def __str__(self):
        return self.user.email
    
    
    class Meta:
        verbose_name_plural = "Customer Profile"
    
    

def create_profile(sender, instance, created, **kwargs):
    if created and instance.is_active == True:
        Profile.objects.create(user=instance)

User = get_user_model()
post_save.connect(create_profile, sender=User)

