from django import forms
# from django.contrib.auth.models import User
from .models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *

class RegisterForm(UserCreationForm):
    # phone = forms.CharField(max_length=30,label='',
    #            widget=forms.TextInput(attrs={
    #             "class":"form-control",
    #             'autofocus':None,
    #             'id':'phone',
    #             "placeholder":"Enter your phone number .."
    #            }) 
    #            )
    # first_name = forms.CharField(max_length=30,label='',
    #            widget=forms.TextInput(attrs={
    #                "class":"form-control",
    #                "placeholder":"Enter your full name.."
    #            }) 
    #            )
    # email = forms.EmailField(required=False,label='',
    #         widget=forms.TextInput(attrs={
    #             "class":"form-control",
    #             "placeholder":"Enter your email..(optional)"
    #         })
    #         )
    # password1 = forms.CharField(max_length=30,label='',
    #            widget=forms.PasswordInput(attrs={
    #                "class":"form-control",
    #                "placeholder":"Password"
    #            }) 
    #            )
    # password2 = forms.CharField(max_length=30,label='',
    #            widget=forms.PasswordInput(attrs={
    #                "class":"form-control",
    #                "placeholder":"Password confirmation"
    #            }) 
    #            )

    # terms_and_conditions = forms.CharField(max_length=30,label='By signing up you agree to our terms and conditions.',
    #            widget=forms.CheckboxInput(attrs={
    #                "class":"form-check-input tc_checkbox",          
    #            }) 
    #            )

    class Meta:
        model=User
        fields =['email', 'password1', 'password2']
    
    # def __init__(self, *args, **kwargs):
    #     super(RegisterForm, self).__init__(*args, **kwargs)
    #     self.fields['phone'].widget.attrs.pop("autofocus", None)



# class UpdateRegisterForm(forms.ModelForm):
#     class Meta:
#         model=User
#         fields =[ 'username', 'first_name', 'last_name', 'email']

# class UpdateProfileForm(forms.ModelForm):
#     date_of_birthday = forms.DateField(required=False,
#         widget=forms.TextInput( attrs={
#         "type":"date",
#     })
#     )
#     class Meta:
#         model = Profile
#         fields = ['image','date_of_birthday','phone','permanent_address','present_address']




# class UserLoginForm(AuthenticationForm):
#     class Meta:
#         model = User
#         fields = ('email', 'password')
    