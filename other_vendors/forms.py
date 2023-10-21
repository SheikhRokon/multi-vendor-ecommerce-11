from django import forms
from django.contrib.auth.forms import UserChangeForm
from userapp.models import User
from .models import *


class RegistrationForm(UserChangeForm):
    class meta:
        models = User
        fields = ['email', 'password1', 'password2']
        
class VendorInformationForm(forms.ModelForm):
    class Meta:
        model = VendorInformation
        exclude = ['user','is_verified']
        
class VendorInformationFormUpdate(forms.ModelForm):
    class Meta:
        model = VendorInformation
        exclude = ['user']
        
            
            
    

        