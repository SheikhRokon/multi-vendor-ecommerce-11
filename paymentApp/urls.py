from django.urls import path
from .views import *

urlpatterns = [
    path("checkout/",CheckOutView.as_view(), name="Check-Out"),
    path("address/",ShippingAdressView.as_view(), name="address"),
    # path("sslc/statuse/", sslc_status, name="status"),
    # path("sslc/complete/<val_id>/<tran_id>/", sslc_complete, name="sslc-complete"),
    # path('payment/<payment_option>/',StripePaymentView.as_view(), name='stripe-payment'),
    # Nagad
    # path('initiate_payment/<invoice_number>/<pg_public_key>/<merchant_private_key>/<base_url>', initiate_payment, name='initiate_payment'),
    path('initiate_payment/', initiate_payment, name='initiate_payment'),
    
    
    path('bkash_payment', create_bkash_payment, name='bkash-payment'),
    path('execute_bkash', execute_bkash_payment, name='execute-bkash'),
    path('bkash_payment_list', bkash_payment_list, name='bkash_payment-list'),
    path('bkash_search_transaction/<str:trxID>',bkash_search_transaction, name='bkash_search-transaction'),
    path('bkash_payment_query/<str:paymentID>',bkash_payment_query, name='bkash_payment-query'),
    path('bkash_payment_refund/<str:paymentID>',bkash_payment_refund, name='bkash_payment-refund'),
    path('bkash_payment_refund_list', bkash_payment_refund_list, name='bkash_payment_refund-list'),

]
