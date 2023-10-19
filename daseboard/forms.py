from email.policy import default
from django import forms
from store.models import *
from paymentApp.models import *
from django.forms import inlineformset_factory
from django.utils import timezone
from ckeditor_uploader.widgets import CKEditorUploadingWidget 
# from userapp.models import User,Profile
from django.forms import ModelChoiceField

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields ='__all__'
        
# product add inline formset

class ProductForm(forms.ModelForm):
    aditional_discription = forms.CharField(required=False,widget=forms.Textarea(attrs={
        'class':'form-control p-20',
        'rows':"4"
    }))
    discription =forms.CharField(widget=CKEditorUploadingWidget(attrs={
        'class':'form-control p-20',
        'rows':"4"
    }))
    flash_sale_add_and_expire_date = forms.DateTimeField(required=False, disabled=False,
                                          widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    
    class Meta:
        model = Product
        exclude = ['user']

class ImageForm(forms.ModelForm):

    class Meta:
        model = ProductImgGallery
        fields = '__all__'


class VariantForm(forms.ModelForm):
    VAR_CATEGORIES = ( 
        ('', '--select variation type--'), 
        ('size', 'size'), 
        ('color', 'color'), 
        )
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control'
        }))
    category = forms.ChoiceField(choices=VAR_CATEGORIES,widget=forms.Select(attrs={
        'class':'form-control'
        }))
        
    class Meta:
        model = Variation
        fields = '__all__'


VariantFormSet = inlineformset_factory(
    Product, Variation, form=VariantForm,
    extra=1, can_delete=True, can_delete_extra=True
)
ImageFormSet = inlineformset_factory(
    Product, ProductImgGallery, form=ImageForm,
    extra=1, can_delete=True, can_delete_extra=True
)


class CategoryAddForm(forms.ModelForm):
    category_name = forms.CharField(max_length=100,
            widget=forms.TextInput(attrs={
                'placeholder':'categorie name'
            }) 
            )
    parent = ModelChoiceField(required=False,queryset=ProductCategory.objects.all(),empty_label="Select parent category",widget=forms.Select(attrs={
        'class':'form-control'
    # parent = ModelChoiceField(required=False,queryset=ProductCategory.objects.filter(parent__isnull=True),empty_label="Select parent category",widget=forms.Select(attrs={
    #     'class':'form-control'
        }))
    class Meta:
        model = ProductCategory
        fields =['category_name','parent','img']


class BrandAddForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields =['name','image']

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields ='__all__'


class LogoForm(forms.ModelForm):
    class Meta:
        model = WebsiteLogo
        fields ='__all__'


class CouponAddForm(forms.ModelForm):
    valid_from = forms.DateTimeField(required=True, disabled=False,
                                          widget=forms.DateTimeInput(attrs={'type':'datetime-local'}),
                                          error_messages={'required': "This field is required."})
    valid_to = forms.DateTimeField(required=True, disabled=False,
                                          widget=forms.DateTimeInput(attrs={'type':'datetime-local'}),
                                          error_messages={'required': "This field is required."})
    class Meta:
        model = Coupon
        fields = ['code','amount','valid_from','valid_to','max_value']


class FlashsaleForm(forms.ModelForm):
    FlashSaleOn_date = forms.DateTimeField(required=True, disabled=False,
                                          widget=forms.DateTimeInput(attrs={'type':'datetime-local'}),
                                          error_messages={'required': "This field is required."})
    FlashSale_expire_date = forms.DateTimeField(required=True, disabled=False,
                                          widget=forms.DateTimeInput(attrs={'type':'datetime-local'}),
                                          error_messages={'required': "This field is required."})
    class Meta:
        model = FlashSale
        fields = ['title','FlashSaleOn_date','FlashSale_expire_date']


class OrderupdateForm(forms.ModelForm): 
    order_complate_date = forms.DateTimeField(required=False, disabled=False,
                                        widget=forms.DateTimeInput(attrs={
                                            'type':'date',
                                            "class":"form-control",
                                            }),
                                        error_messages={'required': "This field is required."})

    class Meta:
        model = Order
        fields = '__all__'


class OrderShippingAddressUpdateForm(forms.ModelForm): 
    full_address = forms.CharField(required=False,widget=forms.Textarea(attrs={
        'class':'form-control p-20',
        'rows':"4"
    }))
    order_note = forms.CharField(required=False,widget=forms.Textarea(attrs={
        'class':'form-control p-20',
        'rows':"4"
    }))
    class Meta:
        model = ShipingAddress
        fields = '__all__'

class CampaignCategoryForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = '__all__'

class CampaignProductForm(forms.ModelForm):
    class Meta:
        model = CampaignProduct
        fields = '__all__'

class DealOfTheDayProductForm(forms.ModelForm):
    class Meta:
        model = DealOfTheDayProduct
        fields = '__all__'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = '__all__'


class ContactForm(forms.ModelForm):
    class Meta:
        model = ConductData
        fields = '__all__'

# Privacy Policy
# Terms and conditions
# Our Mission & Vision
# Returns Policy
# Shipping and Delivery

class PrivacyPolicyForm(forms.ModelForm):
    all_information =forms.CharField(widget=CKEditorUploadingWidget(attrs={
        'class':'form-control p-20',
        'rows':"4"
    }))
    class Meta:
        model = PrivacyPolicy
        fields = '__all__'


class TermsAndConditionsForm(forms.ModelForm):
    all_information =forms.CharField(widget=CKEditorUploadingWidget(attrs={
        'class':'form-control p-20',
        'rows':"4"
    }))
    class Meta:
        model = TermsAndConditions
        fields = '__all__'

class MissionForm(forms.ModelForm):
    all_information =forms.CharField(widget=CKEditorUploadingWidget(attrs={
        'class':'form-control p-20',
        'rows':"4"
    }))    
    class Meta:
        model = Mission
        fields = '__all__'

class VisionForm(forms.ModelForm):
    all_information =forms.CharField(widget=CKEditorUploadingWidget(attrs={
        'class':'form-control p-20',
        'rows':"4"
    }))    
    class Meta:
        model = Vision
        fields = '__all__'

class Returns_PolicyForm(forms.ModelForm):
    all_information =forms.CharField(widget=CKEditorUploadingWidget(attrs={
        'class':'form-control p-20',
        'rows':"4"
    }))    
    class Meta:
        model = Returns_Policy
        fields = '__all__'

class ShippingAndDeliveryForm(forms.ModelForm):
    all_information =forms.CharField(widget=CKEditorUploadingWidget(attrs={
        'class':'form-control p-20',
        'rows':"4"
    }))    
    class Meta:
        model = ShippingAndDelivery
        fields = '__all__'


class AboutUsForm(forms.ModelForm):
    all_information =forms.CharField(widget=CKEditorUploadingWidget(attrs={
        'class':'form-control p-20',
        'rows':"4"
    }))    
    class Meta:
        model = AboutUs
        fields = '__all__'




class ImageAddForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput(attrs={
            'id':"upload"
        })
        )
    class Meta:
        model = ImageGallery
        fields = ['title','image']

class VideoAddForm(forms.ModelForm):
    
    class Meta:
        model = VideoGallery
        fields = '__all__'

class PercelForm(forms.ModelForm):
    parcel_weight = forms.CharField(required=False,widget=forms.NumberInput(attrs={
       
    }))
    class Meta:
        model = ProductPercel
        fields = ['delivery_area','parcel_weight']





