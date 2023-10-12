from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


class Country(models.Model):
    name=models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class Division(models.Model):
    name=models.CharField(max_length=100)
    country=models.ForeignKey(Country,on_delete=models.CASCADE, related_name='divisions')
    def __str__(self):
        return self.name
    
class District(models.Model):
    name=models.CharField(max_length=100)
    division=models.ForeignKey(Division,on_delete=models.CASCADE, related_name='districts')
    def __str__(self):
        return self.name
    
class SubDistrict(models.Model):
    name=models.CharField(max_length=100)
    district=models.ForeignKey(District,on_delete=models.CASCADE, related_name='subdistricts')
    def __str__(self):
        return self.name
    
    
    
class VendorInformation(models.Model):
    ID_type = [
        ('NID','NID'), 
        ('Passport', 'Passport'), 
        ('Driving Licence', 'Driving Licence')
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vendorinformation")
    phone = models.CharField(max_length=16, blank=True, null=True)
    id_type = models.CharField(max_length=20, choices=ID_type, default='NID')
    first_and_last_name = models.CharField(max_length=25)
    vendor_image = models.ImageField(upload_to='vendor_image/', blank=True, null=True)
    Nid_number = models.CharField(max_length=20)
    NID_copy_1 = models.FileField()
    NID_copy_2 = models.FileField()
    
    shop_name = models.CharField(max_length=120)
    address = models.CharField(max_length=300)
    country = models.CharField(max_length=20)
    division = models.CharField(max_length=20)
    district = models.CharField(max_length=20)
    upazila = models.CharField(max_length=20)
    
    warehouse_address = models.BooleanField(default=True)   
    w_address = models.CharField(max_length=300, blank=True,null=True)
    w_division = models.CharField(max_length=20,blank=True,null=True)
    w_district = models.CharField(max_length=20,blank=True,null=True)
    w_upazila = models.CharField(max_length=20,blank=True,null=True)
    
    return_address = models.BooleanField(default=True)
    r_address = models.CharField(max_length=300, blank=True,null=True)
    r_division = models.CharField(max_length=20,blank=True,null=True)
    r_district = models.CharField(max_length=20,blank=True,null=True)
    r_upazila = models.CharField(max_length=20,blank=True,null=True)
    
    account_title = models.CharField(max_length=30)
    account_number = models.CharField(max_length=30)
    bank_name = models.CharField(max_length=30)
    bank_branch_name = models.CharField(max_length=30)
    routing_number = models.CharField(max_length=30)
    cheque_copy = models.FileField()
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Vendor Profile"

    def __str__(self):
        return self.user.email
    
    
# def create_profile(sender, instance, created, **kwargs):
#     if kwargs['created'] and instance.is_vendor==True:
#         VendorInformation.objects.create(user=kwargs['instance'])
# post_save.connect(create_profile,sender=settings.AUTH_USER_MODEL)


from django.contrib.auth import get_user_model

def create_profile(sender, instance, created, **kwargs):
    if created and instance.is_vendor == True:
        VendorInformation.objects.create(user=instance)

User = get_user_model()
post_save.connect(create_profile, sender=User)

    

