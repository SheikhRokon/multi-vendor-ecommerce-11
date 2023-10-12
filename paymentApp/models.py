from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.conf import settings

# Create your models here.
class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=50, blank=True, null=True)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    city = models.CharField(max_length = 150)
    state = models.CharField(max_length = 150) 
    zip =models.CharField(max_length=100)
    phone =models.CharField(max_length=11)
    email = models.EmailField()
    order_note = models.TextField()     
    
    def __str__(self):
        return self.user.username
        
    # def is_fully_filled(self):
    #     field_names = [f.name for f in self._meta.get_fields()]
    #     for field_name in field_names:
    #         value = getattr(self, field_name)
    #         if value is None or value == '':
    #             return False
    #     return True

    class Meta:
        verbose_name_plural='BillingAddress'

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class ShipingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    phone =models.CharField(max_length=15)
    Shiping_Area_Type =(
        ('Inside Dhaka','Inside Dhaka'),
        ('Outside Dhaka','Outside Dhaka'),
        ('Only Chittagong District','Only Chittagong District')
    )
    shiping_area = models.CharField(max_length=100, choices=Shiping_Area_Type)
    full_address = models.TextField()     
    order_note = models.TextField(blank=True, null=True)     
    
    def __str__(self):
        return self.user.username


class BkashPayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    paymentID  = models.CharField(max_length = 150)
    createTime = models.CharField(max_length=150)
    orgName  = models.CharField(max_length = 150)
    transactionStatus  = models.CharField(max_length = 150)
    amount = models.CharField(max_length = 150)
    currency = models.CharField(max_length = 150)
    intent = models.CharField(max_length = 150)
    merchantInvoiceNumber = models.CharField(max_length = 150)
    
    class Meta:
        verbose_name = 'BkashPayment'
        verbose_name_plural = 'BkashPayments'

    def __str__(self):
        return self.paymentID

class BkashPaymentExecute(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    paymentID  = models.CharField(max_length = 150)
    createTime  = models.CharField(max_length = 150)
    updateTime  = models.CharField(max_length = 150)
    trxID  = models.CharField(max_length = 150)
    transactionStatus  = models.CharField(max_length = 150)
    amount  = models.CharField(max_length = 150)
    currency  = models.CharField(max_length = 150)
    intent  = models.CharField(max_length = 150)
    merchantInvoiceNumber  = models.CharField(max_length = 150)
    customerMsisdn  = models.CharField(max_length = 150)
    

    class Meta:
        verbose_name_plural = 'BkashPaymentExecute'

    def __str__(self):
        return  self.paymentID

class BkashPaymentRefund(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    originalTrxID = models.CharField(max_length = 150)
    refundTrxID = models.CharField(max_length = 150)
    transactionStatus = models.CharField(max_length = 150)
    amount = models.CharField(max_length = 150)
    completedTime = models.CharField(max_length = 150)
    currency = models.CharField(max_length = 150)
    charge = models.CharField(max_length = 150)

    class Meta:
        verbose_name_plural = 'BkashPaymentRefund'

    def __str__(self):
        return self.originalTrxID



