from store.models import *


def order_count(request):
    order_count = Order.objects.filter(order_read_status=False).count()
    context ={
        'order_count':order_count
    }
    return context


def order_list(request):
    order_list = Order.objects.filter(order_read_status=False)
    context ={
        'order_list':order_list
    }
    return context

def contact_data_count(request):
    contact_data_count = ConductData.objects.filter(view_status=False).count()
    context ={
        'contact_data_count':contact_data_count
    }
    return context


def contact_data_list(request):
    contact_data_list = ConductData.objects.filter(view_status=False)
    context ={
        'contact_data_list':contact_data_list
    }
    return context

def rating_list_view(request):
    rating_review = ProductReview.objects.filter(approve_status=False)
    context={
        'rating_review':rating_review
    }
    return context

def order_information(request):
    order_information = Order.objects.filter(order_status='complete')
    total_sale = 0
    total_purchase_price = 0
    for x in order_information:
        total_sale = total_sale + x.get_total()        
        total_purchase_price = total_purchase_price + x.get_purchase_price_total()

    total_revenue = total_sale - total_purchase_price

    context={
        'order_information':order_information,
        'total_sale':total_sale,
        'total_revenue':total_revenue
    }
    # get_purchase_price_total
    return context
