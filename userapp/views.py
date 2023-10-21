from django.shortcuts import render
from .forms import *
from django.contrib import messages
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

from uniform import *

def register(request):
    if request.method =='POST':
        form =RegisterForm(request.POST)
        if form.is_valid():
            # form.instance.username = f'{random.randrange(10000000)}'
            # form.instance.username = form.instance.phone
            user = form.save(commit=False)
            user.is_customer = True
            user.save()
            # phone =form.cleaned_data.get('phone')      
            # messages.success(request,f'Account created for {phone}! You are now able to login')
            messages.success(request,' Registration Successfully')
            return redirect('customer-login')
    else:
        form =RegisterForm()
    return render(request, 'userapp/register.html', {'form':form})



def customer_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_customer == True:
            login(request, user)
            return redirect('profile-dashboard')
        elif user is not None and user.is_vendor == True: 
            login(request, user)
            return redirect('dashboard-home')
        elif user is not None and user.is_staff == True: 
            login(request, user)
            return redirect('dashboard-home')
    return render(request, 'userapp/login.html')


@login_required
def profile(request):
    return render(request, 'userapp/profile.html')

@login_required
def profileupdate(request):

    if request.method == 'POST':
        u_form = UpdateRegisterForm(request.POST, instance=request.user)
        p_form = UpdateProfileForm(request.POST,request.FILES,instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        u_form =  UpdateRegisterForm(instance=request.user)
        p_form = UpdateProfileForm(instance=request.user.profile)

    context = {

        'u_form': u_form,
        'p_form': p_form,
    }

    return render(request, 'userapp/profileupdate.html', context)





