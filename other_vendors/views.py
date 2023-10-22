from django.shortcuts import get_object_or_404, render,redirect
import json
from .models import *
from django.contrib.auth import login
from .forms import *
from userapp.forms import *
from userapp.urls import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm


def vendor_registaion_step_1(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_vendor = True
            user.save()
            messages.success(request,' Registration Successfully')
            return redirect('vendor_login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")   
    form = RegisterForm()
    return render(request, 'other_vendors/vendor_re_step_1.html', {'form': form})

def vendor_login(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email = email, password=password)
        if user is not None and user.is_vendor == True: 
            login(request, user)
            return redirect('dashboard-home')
        else:
            messages.error(request, 'Invalid credentials or you are not a vendor.')
            return render(request, 'other_vendors/vendor_login.html', {'form': form})

    else:
        return render(request, 'other_vendors/vendor_login.html', {"form": form})
    

def vendor_profile_update(request):
    try:
        # Retrieve the existing VendorInformation instance for the logged-in user
        vendor_profile = VendorInformation.objects.get(user=request.user)
    except VendorInformation.DoesNotExist:
        vendor_profile = None

    if request.method == 'POST':
        if vendor_profile:
            # If a profile exists, populate the form with the current data
            form = VendorInformationForm(request.POST, request.FILES, instance=vendor_profile)
        else:
            # If no profile exists, create a new instance
            form = VendorInformationForm(request.POST, request.FILES)

        if form.is_valid():
            vendor_profile = form.save(commit=False)
            vendor_profile.user = request.user
            vendor_profile.save()
            messages.success(request, 'Profile Updated Successfully')
            return redirect('vendor_pro')

    else:
        if vendor_profile:
            # If a profile exists, prepopulate the form with the current data
            form = VendorInformationForm(instance=vendor_profile)
        else:
            form = VendorInformationForm()

    id_types = VendorInformation.ID_type
    context = {
        'form': form,
        'id_types': id_types,
    }

    return render(request, 'other_vendors/vendor_full_info.html', context)


def vendor_registaion_step_2(request):
    return render(request, 'other_vendors/vendor_re_step_2.html')

@login_required
def vendor_pro(request):
    return render(request, 'other_vendors/vendor_pro.html')

def vendor_dashvoard(request):
    return render(request, 'other_vendors/vendor_dashvoard.html')

def vendor_address(request):
    country = Country.objects.all().order_by('name')
    country_list = list(country.values('name','id'))
    country_list = json.dumps(country_list)
    
    division = Division.objects.all().order_by('name')
    division_list = list(division.values('name','country__name','id'))
    division_list = json.dumps(division_list)
    
    district = District.objects.all().order_by('name')
    district_list = list(district.values('name','division__name','id'))
    district_list = json.dumps(district_list)
    
    subdistrict = SubDistrict.objects.all().order_by('name')
    subdistrict_list = list(subdistrict.values('name','district__name','id'))
    subdistrict_list = json.dumps(subdistrict_list)
    
    context ={
        'country_list': country_list,
        'division_list': division_list,
        'district_list': district_list,
        'subdistrict_list': subdistrict_list  
    }
    return render(request, 'other_vendors/vendor_address.html', context)

def vendor_id_verify(request):
    return render(request, 'other_vendors/vendor_id_verify.html')

def verify_bank_account(request):
    return render(request, 'other_vendors/verify_bank_account.html')



def vendor_pro_update(request):
    profile = get_object_or_404(VendorInformation)
    form = VendorInformationForm(instance=profile) 
    if request.method == 'POST':
        form = VendorInformationForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated')
            return redirect('dashboard-home')  
    context = {
        'form': form,
    }
    return render(request, 'other_vendors/profile_update.html', context)






