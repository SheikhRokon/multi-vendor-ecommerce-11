from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from .models import *
from store.models import *
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.urls import reverse
#ssl commerz intregation
from django.conf import settings
import json
# from sslcommerz_python.payment import SSLCSession
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .models import BkashPayment
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from userapp.decorators import *
# Create your views here.
from django.utils.decorators import method_decorator
from django.utils.html import format_html

# stripe
# import stripe
# stripe.api_key = "sk_test_51HEtKGL8BxQy57KfDDoOgx9HkwDZXH16fTSh5q0pty24ndg9o3RBdfvQFVNKHOgPHhhRq2pieS8aw7gGWBgObMQI00EuUjNyUc"

@method_decorator([login_required], name='dispatch')
class ShippingAdressView(View):
    def get(self, request, *args, **kwargs):
        try:
            form = SippingAddressForm()
            order = Order.objects.get(user=request.user, ordered=False)
            context = {
                'form': form,
                'order':order,
            }
            return render(request, 'address.html', context)
        except ObjectDoesNotExist:
            messages.warning(request, 'You have no active order')
            return redirect('/')

    def post(self, request, *args, **kwargs):
        form = SippingAddressForm(request.POST)
        payment_obj = Order.objects.filter(user=request.user, ordered=False)[0]
        payment_form = PaymentMethodForm(instance=payment_obj)
        
        if request.method == 'post' or request.method == 'POST':
            form = SippingAddressForm(request.POST)
            if form.is_valid():
                full_name =form.cleaned_data.get('full_name')
                shiping_area =form.cleaned_data.get('shiping_area')
                phone =form.cleaned_data.get('phone')
                full_address =form.cleaned_data.get('full_address')
                order_note =form.cleaned_data.get('order_note')

                shipping_address  = ShipingAddress(
                    user=request.user,
                    full_name=full_name,
                    shiping_area=shiping_area,
                    phone=phone,
                    full_address=full_address,
                    order_note=order_note
                )
                shipping_address.save()
                payment_obj.shipping_address =shipping_address
                payment_obj.save()
                return redirect('Check-Out')

@method_decorator([login_required], name='dispatch')
class CheckOutView(View):
    def get(self, request, *args, **kwargs):
        try:
            payment_method = PaymentMethodForm()
            order = Order.objects.get(user=request.user, ordered=False)
            context = {
                'payment_method': payment_method,
                'order': order,
            }
            return render(request, 'checkout.html', context)
        except ObjectDoesNotExist:
            messages.warning(request, 'You have no active order')
            return redirect('/')

    def post(self, request, *args, **kwargs):
        global pay_method
        
        payment_obj = Order.objects.filter(user=request.user, ordered=False).first()
        if payment_obj is not None:
            if request.method == 'POST':
                pay_form = PaymentMethodForm(request.POST, instance=payment_obj)
                if pay_form.is_valid():
                    pay_method = pay_form.save()
                    if pay_method.payment_option == 'Cash On Delivery':
                        # order_qs = Order.objects.filter(user=request.user, ordered=False)
                        # order = order_qs.first()
                        # order.ordered = True
                        # order.orderId = order.id
                        # order.total_order_amount = order.total()
                        # order.due_amount = order.total_paid_amount()
                        # order.paymentId = pay_method.payment_option

                        # order_items = OrderItem.objects.filter(user=request.user, ordered=False)
                        # for order_item in order_items:
                        #     order_item.ordered = True
                        #     stock_manage = order_item.item.stock_quantity - order_item.quantity
                        #     order_item.save()
                        #     get_prd = Product.objects.get(id=order_item.item.id)
                        #     get_prd.stock_quantity = stock_manage
                        #     get_prd.save()

                        # order.save()
                        # messages.success(request, "Your order was successful")
                        return redirect('bkash-payment')
                    elif pay_method.payment_option == 'Bkash':
                    #   return format_html('<button id="bKash_button">{}</button>')
                        return redirect('bkash-payment')
                    else:
                        return redirect('Check-Out')
            else:
                return redirect('Check-Out')
        else:
            messages.warning(request, 'No active order found')
            return redirect('/')


# Bkash Payment

import requests
from django.views.decorators.csrf import csrf_exempt
app_key = "CUkwm3KsKSvyGA6YINNzpwahtc"
app_secret = "8xJDdUIJPvhgPJIbwkmSVT5b6CfhXqcAFwfnBhyOe0WVi9JMyp8m"


def grant_token_function():
    token_url = "https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized/checkout/token/grant"

    payload = {
    "app_key":f"{app_key}",
    "app_secret":f"{app_secret}"
    }

    headers = {
        "Content-Type":"application/json",
        "Accept":"application/json",
        "username":"01701069706",
        "password":"v^oKwJ9DBS["
    }

    token_response = requests.post(token_url, json=payload, headers=headers)
    token =json.loads(token_response.content)
   # print(token)
    id_tokens = token.get('id_token')
    return id_tokens

id_token = grant_token_function()

def pay(request): 
    return render(request, 'bkash-payment.html')

from django.http import JsonResponse

@login_required
@csrf_exempt
def create_bkash_payment(request, *args, **kwargs):
    global pay_method
    global order
    id_token = grant_token_function()
    create_url = "https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized/checkout/create"
    order = Order.objects.get(user=request.user, ordered=False)
    
    if pay_method.payment_option == 'Cash On Delivery':
        payload = json.dumps({
            "mode": "0011",
            "payerReference": "N/A",
            "callbackURL":"http://127.0.0.1:8000/execute_bkash",
            "amount":f"{order.only_shiping_charge_payment()}",
            "currency": "BDT",
            "intent": "sale",
            "merchantInvoiceNumber":f"{order.id}",
        })
    else:
        payload = json.dumps({
            "mode": "0011",
            "payerReference": "N/A",
            "callbackURL":"http://127.0.0.1:8000/execute_bkash",
            "amount":f"{order.total()}",
            "currency": "BDT",
            "intent": "sale",
            "merchantInvoiceNumber":f"{order.id}",
        })   

    headers = {
        "Accept": "application/json",
        "Authorization": f"{id_token}",
        "X-APP-Key":f"{app_key}",
        "Content-type": "application/json"
    }

    create_response = requests.post(create_url, data=payload, headers=headers)

    response =json.loads(create_response.content)
    # print(response)
    # id_tokens = token.get('id_token')
    # print(create_response.text)
    # return render(request, 'bkash-payment1.html',{'response':response})
    
    PaymentId=response['paymentID'] 
    createTime=response['paymentCreateTime']
    # orgName = response['orgName']
    transactionStatus = response['transactionStatus']
    amount = response['amount']
    currency = response['currency']
    intent = response['intent']
    merchantInvoiceNumber = response['merchantInvoiceNumber']
    
    BkashPayment.objects.create(user=request.user,paymentID = PaymentId, createTime=createTime, transactionStatus =  transactionStatus , amount=amount, currency= currency,  intent= intent,merchantInvoiceNumber=merchantInvoiceNumber )
    
    return redirect(response['bkashURL'])

@login_required
@csrf_exempt
def execute_bkash_payment(request):
    
    id_token = grant_token_function()
    length = BkashPayment.objects.filter(user=request.user).count()
    Id = BkashPayment.objects.filter(user=request.user)[length-1].paymentID
    print(Id)
    url = f"https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized/checkout/execute"
    
    payload = {
        "paymentID":f"{Id}",
    }

    headers = {
        "Accept": "application/json",
        "Authorization": f"{id_token}",
        "X-APP-Key": f"{app_key}"
    }

    response_create = requests.post(url, json=payload, headers=headers)

    try:
        response = response_create.json()
    except json.JSONDecodeError:
        messages.error(request, "Invalid JSON response from bKash.")
        return JsonResponse({"error": "Invalid JSON response from bKash."})
   

    if response.get('errorCode') and response.get('errorCode') != '0000':
        text = response.get('errorMessage')
        messages.error(request, f"{text}") 
    else:
        paymentID = response.get('paymentID') 
        
        if paymentID is None:      
            messages.error(request, "PaymentID is missing in the response.")
            return JsonResponse({"error": "PaymentID is missing in the response"})
        
        paymentID=response.get('paymentID')
        createTime=response.get('createTime')
        # updateTime = response.get('updateTime')
        trxID = response.get('trxID')
        transactionStatus = response.get('transactionStatus')
        amount = response.get('amount')
        currency = response.get('currency')
        intent = response.get('intent')
        paymentExecuteTime = response.get('paymentExecuteTime')
        merchantInvoiceNumber = response.get('merchantInvoiceNumber')
        customerMsisdn = response.get('customerMsisdn')
        customerMsisdn = response.get('payerReference')
    
        BkashPaymentExecute.objects.create(user=request.user, paymentID=paymentID, createTime=paymentExecuteTime, trxID=trxID, transactionStatus=transactionStatus , amount=amount, currency=currency,  intent=intent, merchantInvoiceNumber=merchantInvoiceNumber, customerMsisdn=customerMsisdn)
        
        if pay_method.payment_option == 'Cash On Delivery': 
            order_qs = Order.objects.filter(user=request.user, ordered=False)
            order = order_qs.first()
            order.ordered = True
            order.orderId = order.id
            order.total_order_amount = order.total()
            order.due_amount = order.total_paid_amount() - order.only_shiping_charge_payment()
            order.paid_amount = order.only_shiping_charge_payment()
            order.paymentId = pay_method.payment_option

            order_items = OrderItem.objects.filter(user=request.user, ordered=False)
            for order_item in order_items:
                order_item.ordered = True
                stock_manage = order_item.item.stock_quantity - order_item.quantity
                order_item.save()
                get_prd = Product.objects.get(id=order_item.item.id)
                get_prd.stock_quantity = stock_manage
                get_prd.save()

            order.save()
            messages.success(request, "Your order was successful")
            return redirect('order-summary')
        else:
            print('bkash')
            order_qs = Order.objects.filter(user=request.user, ordered=False)
            order = order_qs[0]
            order.ordered = True
            order.orderId = order.id
            order.total_order_amount = order.total()
            order.paid_amount = order.total()
            order.paymentId = 'Bkash'
            

            order_items = OrderItem.objects.filter(user=request.user, ordered=False)
            for order_item in order_items:
                order_item.ordered = True
                stock_manage = order_item.item.stock_quantity - order_item.quantity
                # print(stock_manage)
                # order_item.item.stock_quantity = stock_manage
                order_item.save()
                # print(order_item.item.id)
                get_prd = Product.objects.get(id=order_item.item.id)
                get_prd.stock_quantity = stock_manage
                get_prd.save()

            order.save()
            
            messages.success(request, "Your Payment successful done")
            return redirect('order-summary')
            
    return JsonResponse(response)


@login_required
@daseboard_required
def bkash_payment_list(request):
    payment_list = BkashPaymentExecute.objects.all().order_by('-id')

    context ={
        'payment_list':payment_list
    }
    return render(request, 'paymentApp/bkash/payment-list.html',context)


@login_required
@daseboard_required
def bkash_search_transaction(request,trxID):
    payment_list = BkashPaymentExecute.objects.get(trxID=trxID)
    trxID = payment_list.trxID
    id_token = grant_token_function()

    url = f'https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized/checkout/general/searchTransaction{trxID}'

    headers = {
        "accept": "application/json",
        "Authorization": f"{id_token}",
        "X-APP-Key": f"{app_key}"
    }

    response_create = requests.get(url, headers=headers)
    response=json.loads(response_create.content)

    print(url)
    print(response)

    return render(request, 'paymentApp/bkash/serach-transaction.html',{'response':response})

@login_required
@daseboard_required
def bkash_payment_query(request,paymentID):
    payment_list = BkashPaymentExecute.objects.get(paymentID=paymentID)
    paymentID = payment_list.paymentID
    id_token = grant_token_function()

    url = f'https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized/checkout/payment/status{paymentID}'

    headers = {
        "accept": "application/json",
        "Authorization": f"{id_token}",
        "X-APP-Key": f"{app_key}"
    }

    response_create = requests.get(url, headers=headers)
    response=json.loads(response_create.content)

    print(url)
    print(response)

    return render(request, 'paymentApp/bkash/payment-query.html',{'response': response})


@login_required
@daseboard_required
def bkash_payment_refund(request, paymentID):
    global pay_method
    try:
        payment_list = BkashPaymentExecute.objects.get(paymentID=paymentID)
    except BkashPaymentExecute.DoesNotExist:
        messages.error(request, "Payment not found.")
        return redirect('bkash_payment-list')

    # Obtain necessary parameters from the request or any other source
    id_token = grant_token_function()
    url = 'https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized/checkout/payment/refund'
    
    sku = request.POST.get('sku')
    reason = request.POST.get('reason')
    print(sku, reason)
    payload = {
        "paymentID": payment_list.paymentID,
        "trxID": payment_list.trxID,
        "amount": payment_list.amount,
        "sku": sku,
        "reason": reason,
    }
   
    headers = {
        "accept": "application/json",
        "Authorization": f"{id_token}",
        "X-APP-Key": f"{app_key}"  # Make sure to define app_key somewhere in your code
    }
    try:
        # Make the refund request to bKash API
        response_create = requests.post(url, headers=headers, data=json.dumps(payload))
        response = response_create.json()

        if response.get('errorCode') and response.get('errorCode') != '0000':
            # Handle error case
            error_message = response.get('errorMessage')
            messages.error(request, f"{error_message}")
        else:
            original_trx_id = payment_list.trxID
            print(original_trx_id)

            if original_trx_id is not None:
                # Create BkashPaymentRefund only if originalTrxID is present
                refund_trx_id = response.get('refundTrxID')
                transaction_status = response.get('transactionStatus')
                amount = response.get('amount')
                completed_time = response.get('completedTime')
                currency = response.get('currency')
                charge = response.get('charge')

                # Check if all necessary fields are present
                if refund_trx_id is not None and transaction_status is not None and amount is not None and completed_time is not None and currency is not None and charge is not None:
                    BkashPaymentRefund.objects.create(
                        user=request.user,
                        originalTrxID=original_trx_id,
                        refundTrxID=refund_trx_id,
                        transactionStatus=transaction_status,
                        amount=amount,
                        currency=currency,
                        completedTime=completed_time,
                        charge=charge
                    )

                    messages.success(request, "Your payment refund was successful.")
                    return redirect('bkash_payment_list')
                else:
                    messages.error(request, "One or more required fields are missing in the response.")
            else:
                # Handle case where originalTrxID is missing
                messages.error(request, "OriginalTrxID is missing in the response.")
                print("Response:", response)

    except requests.RequestException as e:
        messages.error(request, f"Error in making the refund request: {e}")

    return render(request, 'paymentApp/bkash/refund.html', {'payment_list': payment_list})


@login_required
@daseboard_required
def bkash_payment_refund_list(request):
    payment_list = BkashPaymentRefund.objects.all()

    context ={
        'payment_list':payment_list
    }
    return render(request, 'paymentApp/bkash/refund-list.html',context)















import base64
import logging
import random
import string
import pytz
from datetime import datetime

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from kombu.utils import json

# from core.utils import get_host_name_ip
## importing socket module
import socket
## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()
merchant_private_key = 'MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCJakyLqojWTDAVUdNJLvuXhROV+LXymqnukBrmiWwTYnJYm9r5cKHj1hYQRhU5eiy6NmFVJqJtwpxyyDSCWSoSmIQMoO2KjYyB5cDajRF45v1GmSeyiIn0hl55qM8ohJGjXQVPfXiqEB5c5REJ8Toy83gzGE3ApmLipoegnwMkewsTNDbe5xZdxN1qfKiRiCL720FtQfIwPDp9ZqbG2OQbdyZUB8I08irKJ0x/psM4SjXasglHBK5G1DX7BmwcB/PRbC0cHYy3pXDmLI8pZl1NehLzbav0Y4fP4MdnpQnfzZJdpaGVE0oI15lq+KZ0tbllNcS+/4MSwW+afvOw9bazAgMBAAECggEAIkenUsw3GKam9BqWh9I1p0Xmbeo+kYftznqai1pK4McVWW9//+wOJsU4edTR5KXK1KVOQKzDpnf/CU9SchYGPd9YScI3n/HR1HHZW2wHqM6O7na0hYA0UhDXLqhjDWuM3WEOOxdE67/bozbtujo4V4+PM8fjVaTsVDhQ60vfv9CnJJ7dLnhqcoovidOwZTHwG+pQtAwbX0ICgKSrc0elv8ZtfwlEvgIrtSiLAO1/CAf+uReUXyBCZhS4Xl7LroKZGiZ80/JE5mc67V/yImVKHBe0aZwgDHgtHh63/50/cAyuUfKyreAH0VLEwy54UCGramPQqYlIReMEbi6U4GC5AQKBgQDfDnHCH1rBvBWfkxPivl/yNKmENBkVikGWBwHNA3wVQ+xZ1Oqmjw3zuHY0xOH0GtK8l3Jy5dRL4DYlwB1qgd/Cxh0mmOv7/C3SviRk7W6FKqdpJLyaE/bqI9AmRCZBpX2PMje6Mm8QHp6+1QpPnN/SenOvoQg/WWYM1DNXUJsfMwKBgQCdtddE7A5IBvgZX2o9vTLZY/3KVuHgJm9dQNbfvtXw+IQfwssPqjrvoU6hPBWHbCZl6FCl2tRh/QfYR/N7H2PvRFfbbeWHw9+xwFP1pdgMug4cTAt4rkRJRLjEnZCNvSMVHrri+fAgpv296nOhwmY/qw5Smi9rMkRY6BoNCiEKgQKBgAaRnFQFLF0MNu7OHAXPaW/ukRdtmVeDDM9oQWtSMPNHXsx+crKY/+YvhnujWKwhphcbtqkfj5L0dWPDNpqOXJKV1wHt+vUexhKwus2mGF0flnKIPG2lLN5UU6rs0tuYDgyLhAyds5ub6zzfdUBG9Gh0ZrfDXETRUyoJjcGChC71AoGAfmSciL0SWQFU1qjUcXRvCzCK1h25WrYS7E6pppm/xia1ZOrtaLmKEEBbzvZjXqv7PhLoh3OQYJO0NM69QMCQi9JfAxnZKWx+m2tDHozyUIjQBDehve8UBRBRcCnDDwU015lQN9YNb23Fz+3VDB/LaF1D1kmBlUys3//r2OV0Q4ECgYBnpo6ZFmrHvV9IMIGjP7XIlVa1uiMCt41FVyINB9SJnamGGauW/pyENvEVh+ueuthSg37e/l0Xu0nm/XGqyKCqkAfBbL2Uj/j5FyDFrpF27PkANDo99CdqL5A4NQzZ69QRlCQ4wnNCq6GsYy2WEJyU2D+K8EBSQcwLsrI7QL7fvQ=='
merchant_id = '683002007104225'
pg_public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAjBH1pFNSSRKPuMcNxmU5jZ1x8K9LPFM4XSu11m7uCfLUSE4SEjL30w3ockFvwAcuJffCUwtSpbjr34cSTD7EFG1Jqk9Gg0fQCKvPaU54jjMJoP2toR9fGmQV7y9fz31UVxSk97AqWZZLJBT2lmv76AgpVV0k0xtb/0VIv8pd/j6TIz9SFfsTQOugHkhyRzzhvZisiKzOAAWNX8RMpG+iqQi4p9W9VrmmiCfFDmLFnMrwhncnMsvlXB8QSJCq2irrx3HG0SJJCbS5+atz+E1iqO8QaPJ05snxv82Mf4NlZ4gZK0Pq/VvJ20lSkR+0nk+s/v3BgIyle78wjZP1vWLU4wIDAQAB'
base_url = 'http://sandbox.mynagad.com:10080'
invoice_number = '178'

# LOGGER = logging.getLogger('payment-module')


def generate_challenge(string_length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(string_length))


def get_timestamp():
    tz = pytz.timezone('Asia/Dhaka')
    now = datetime.now(tz)
    return now.strftime('%Y%m%d%H%M%S')


def encrypt_data_using_public_key(data: str, pg_public_key: str):
    pk = pg_public_key

    try:
        public_key = serialization.load_pem_public_key(pk.encode(), backend=default_backend())
        encrypted_data = public_key.encrypt(data.encode(), padding.PKCS1v15())
        data = base64.b64encode(encrypted_data)
        return data.decode('utf-8'), None
    except Exception as e:
        # LOGGER.error(e)
        print(e)
        return None, e


def decrypt_data_using_private_key(data: str, merchant_private_key: str):
    pk = "-----BEGIN RSA PRIVATE KEY-----\n" + merchant_private_key + "\n-----END RSA PRIVATE KEY-----"

    try:
        private_key = serialization.load_pem_private_key(pk.encode(), password=None, backend=default_backend())
        original_message = private_key.decrypt(data, padding.PKCS1v15())
        return original_message.decode('utf-8'), None
    except Exception as e:
        # LOGGER.error(e)
        print(e)
        return None, e


def generate_signature(data: str, merchant_private_key: str):
    pk = "-----BEGIN RSA PRIVATE KEY-----\n" + merchant_private_key + "\n-----END RSA PRIVATE KEY-----"

    try:
        private_key = serialization.load_pem_private_key(pk.encode(), password=None, backend=default_backend())
        sign = private_key.sign(data.encode(), padding.PKCS1v15(), hashes.SHA256())
        signature = base64.b64encode(sign)
        return signature.decode('utf-8'), None
    except Exception as e:
        # LOGGER.error(e)
        print(e)
        return None, e


def initiate_payment(request):
    now = get_timestamp()

    sensitive_data = {
        'merchantId': merchant_id,
        'datetime': now,
        'challenge': generate_challenge(20)
    }

    sensitive_data_str = json.dumps(sensitive_data)
    encrypted_sensitive_data, err = encrypt_data_using_public_key(sensitive_data_str, pg_public_key)

    if err is not None:
        # LOGGER.error(err)
        print(err)
        return None, err

    signature, err = generate_signature(sensitive_data_str, merchant_private_key)

    if err is not None:
        # LOGGER.error(err)
        print(err)
        return None, err

    data = {
        'dateTime': now,
        'sensitiveData': encrypted_sensitive_data,
        'signature': signature
    }

    # _, host_ip = get_host_name_ip()
    _, host_ip = socket.gethostbyname(hostname)
    

    headers = {
        'Content-Type': 'application/json',
        'X-KM-IP-V4': host_ip,
        'X-KM-Client-Type': 'PC_WEB',
        'X-KM-Api-Version': 'v-0.2.0'
    }

    url = "{}/remote-payment-gateway-1.0/api/dfs/check-out/initialize/{}/{}".format(base_url, merchant_id,
                                                         invoice_number)

    try:
        response = requests.post(url, json.dumps(data), headers=headers, verify=False)
        json_response = response.json()

        if response.status_code != 200:
            # LOGGER.error(json_response)
            print(json_response)
            return None, json_response

        return json_response, None
    except Exception as e:
        # LOGGER.error(e)
        print(e)
        return None, e


# class StripePaymentView(View):
#     def get(self, *args, **kwargs):
#         order = Order.objects.get(user=self.request.user, ordered=False)

#         context ={
#             'order':order,
#         }
#         return render(self.request, 'strippayment.html',context)


#     def post(self, *args, **kwargs):
#         order = Order.objects.get(user=self.request.user, ordered=False)
#         token = self.request.POST.get('stripeToken')
#         amount= int(order.total() * 100)


#         try:
#             charge = stripe.Charge.create(
#                 amount= amount,
#                 currency="usd",
#                 source= token,
#             )
#             #create the payment
#             payment = Payment()
#             payment.stripe_charge_id =charge['id']
#             payment.user = self.request.user
#             payment.amount = order.total()
#             payment.save()

#             # assign the payment to the order
#             order_items = order.items.all()
#             order_items.update(ordered=True)
#             for order_item in order_items:
#                 stock_manage = order_item.item.stock_quantity - order_item.quantity
#                 order_item.save()

#                 get_prd = Product.objects.get(id=order_item.item.id)
#                 get_prd.stock_quantity = stock_manage
#                 get_prd.save()
        
#             order.ordered = True
#             order.payment = payment
#             # order.orderId = val_id
#             order.orderId = order.id
#             order.paymentId = charge['id']
#             order.total_order_amount = order.total()
#             order.paid_amount = order.total()
#             #TODO assign ref code
#             order.save() 
#             messages.success(self.request, "You order was successful")
#             return redirect('/') 
                     
#         except stripe.error.CardError as e:
#             # Since it's a decline, stripe.error.CardError will be caught
#             body = e.json_body
#             err = body.get('error', {})
#             messages.error(self.request, f"{err.get('messages')}")
#             return redirect('/')
#         except stripe.error.RateLimitError as e:
#             # Too many requests made to the API too quickly
#             messages.error(self.request, "Rate limit erro")
#             return redirect('/') 

#         except stripe.error.InvalidRequestError as e:
#             # Invalid parameters were supplied to Stripe's API
#             messages.error(self.request, "invalid parameters")
#             return redirect('/')

#         except stripe.error.AuthenticationError as e:
#             # Authentication with Stripe's API failed
#             # (maybe you changed API keys recently)
#             messages.error(self.request, "Not Authenticated")
#             return redirect('/')

#         except stripe.error.APIConnectionError as e:
#             # Network communication with Stripe failed
#             messages.error(self.request, "Network error")
#             return redirect('/')

#         except stripe.error.StripeError as e:
#             # Display a very generic error to the user, and maybe send
#             # yourself an email
#             messages.error(self.request, "Something is wrong")
#             return redirect('/')
#         except Exception as e:
#             # Send an email to ourselves
#             messages.error(self.request, "Serious erro")
#             return redirect('/')

# @csrf_exempt
# def sslc_status(request):
#     if request.method == 'post' or request.method == 'POST':
#         payment_data = request.POST
#         status = payment_data['status']
#         if status == 'VALID':
#             val_id = payment_data['val_id']
#             tran_id = payment_data['tran_id']

#             return HttpResponseRedirect(reverse('sslc-complete', kwargs={'val_id': val_id, 'tran_id': tran_id}))
#     return render(request, 'status.html')

# def sslc_complete(request, val_id, tran_id):
#     order_qs = Order.objects.filter(user=request.user, ordered=False)
#     order = order_qs[0]
#     order.ordered = True
#     order.orderId = order.id
#     order.paymentId = tran_id
#     order.save()
#     cart_items = OrderItem.objects.filter(user=request.user, ordered=False)
#     for order_item in cart_items:
#         order_item.ordered = True
#         stock_manage = order_item.item.stock_quantity - order_item.quantity
#         order_item.save()

#         get_prd = Product.objects.get(id=order_item.item.id)
#         get_prd.stock_quantity = stock_manage
#         get_prd.save()

#     messages.success(request, "You order was successful")
#     return redirect('/')

import requests
import json

def nagad_payment(request):
    base_url = 'http://sandbox.mynagad.com:10080'
    