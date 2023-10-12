from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from store.models import Order
from .models import *

class SippingAddressForm(forms.Form):
    full_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    phone = forms.CharField(max_length=15,widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    Shiping_Area_Type =(
        ('Inside Dhaka','Inside Dhaka (Delivery within 1-4 Days)'),
        ('Outside Dhaka','Outside Dhaka (Delivery within 1-5 Days)'),
        ('Only Chittagong District','Only Chittagong District (Delivery within 48 hour)'),
    )
    shiping_area = forms.ChoiceField(choices=Shiping_Area_Type,widget=forms.RadioSelect(attrs={
        'onclick':"changeValue(this)"
    }))
    
    full_address = forms.CharField(required=True, widget=forms.Textarea(attrs={
        'class':'form-control',
        'id':"exampleFormControlTextarea1",
        'rows': 2
    }))
    order_note = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class':'form-control',
        'rows': 2
    }))


PAYMENT_CHOICES =(
    ('Cash On Delivery', 'Cash On Delivery'),
    ('Nagad', 'Nagad'),
    ('Rocket', 'Rocket'),
    ('Bkash', 'Bkash'),
    # ('Stripe','Stripe')
)

class PaymentMethodForm(forms.ModelForm):
    payment_option = forms.ChoiceField(widget=forms.RadioSelect(attrs={
        'class':'collapsed'       
    }), choices=PAYMENT_CHOICES)

    class Meta:
        model = Order
        fields = ['payment_option']


class BillingAddressForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    company_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'House number and Street name'
    }))
    apartment_address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Appartments, suite, unit etc ...'
    }))
    country =CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        'class':'form-control',
        'placeholder':'Choice Country...'
    }))
    city = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    state = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    order_note = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class':'form-control',
        'cols': 30,
        'rows': 4
    }))

