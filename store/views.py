# invoice
import os
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, View
from xhtml2pdf import pisa

from paymentApp.models import *
from .forms import *
from .models import *


class ProductView(View):
    def get(self, request):
        banner = Banner.objects.all()
        all_product = Product.objects.filter(
            flash_sale_add_and_expire_date=None).order_by('?')
        flashsale = FlashSale.objects.filter(
            FlashSale_expire_date__gt=datetime.now()).first()
        flashsale_products = Product.objects.filter(
            flash_sale_add_and_expire_date__gt=datetime.now()).order_by('?')
        deal_product = DealOfTheDayProduct.objects.all().order_by('?')
        logo = WebsiteLogo.objects.last()
        context = {
            'banner': banner,
            'all_product': all_product,
            'flashsale': flashsale,
            'flashsale_products': flashsale_products,
            'deal_product': deal_product,
            'logo': logo
        }
        return render(request, 'store/index.html', context)

    def post(self, request):
        pass


class ProductDetail(DetailView):
    model = Product
    template_name = "store/product_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        img = ProductImgGallery.objects.filter(product=self.object.id)

        slug = self.kwargs['slug']
        prod = Product.objects.get(slug=slug)
        related_product = Product.objects.filter(
            categoris=prod.categoris).exclude(slug=slug).order_by('?')
        context['img'] = img
        context['related_product'] = related_product
        return context


class ProductSearchView(View):

    def get(self, request):
        query = request.GET['q']
        search_item = Q(product_name__icontains=query) | Q(price__icontains=query) | Q(
            categoris__category_name__icontains=query) | Q(brand__name__icontains=query)
        products = Product.objects.filter(search_item, Q(flash_sale_add_and_expire_date=None) | Q(
            flash_sale_add_and_expire_date__gt=datetime.now())).order_by('?')

        context = {
            'products': products
        }

        return render(request, 'store/search_product.html', context)


class ProductCategoryFiltering(View):
    def get(self, request, slug):
        cate = get_object_or_404(ProductCategory, slug=slug)
        products = Product.objects.filter(Q(categoris=cate.id) | Q(
            categoris__parent=cate.id), flash_sale_add_and_expire_date=None).order_by('?')

        context = {
            'products': products,
            'cate': cate,
        }
        return render(request, 'store/category.html', context)

    def post(self, request):
        pass


def brandfiltering(request, slug):
    brands = get_object_or_404(Brand, slug=slug)
    products_brands = Product.objects.filter(
        brand=brands.id, flash_sale_add_and_expire_date=None).order_by('?')

    context = {
        'products_brands': products_brands,
        'brands': brands
    }
    return render(request, 'store/brand.html', context)


def pricerangefiltering(request, pk):
    price_ranges = get_object_or_404(PriceRange, pk=pk)
    products = Product.objects.filter(price_range=price_ranges.id)

    context = {
        'products': products,
        'price_ranges': price_ranges,
    }
    return render(request, 'store/products_price_range.html', context)


def campaign_product_filtering(request, pk):
    campaign_cat = get_object_or_404(Campaign, pk=pk)
    campaign_product = CampaignProduct.objects.filter(
        campaign_category=campaign_cat.id, product__flash_sale_add_and_expire_date=None).order_by('?')
    print(campaign_product)
    context = {
        'campaign_product': campaign_product,
        'campaign_cat': campaign_cat
    }
    return render(request, 'store/campaign-product.html', context)


def shop(request):
    products = Product.objects.filter(
        flash_sale_add_and_expire_date=None).order_by('?').order_by('?')

    context = {
        'products': products
    }
    return render(request, 'store/shop.html', context)


def flash_sale(request):
    products = Product.objects.filter(
        flash_sale_add_and_expire_date__gt=datetime.now()).order_by('?')

    context = {
        'products': products
    }
    return render(request, 'store/flash-sale-product.html', context)


def deal_of_the_day(request):
    deal_product = DealOfTheDayProduct.objects.all().order_by('?')

    context = {
        'deal_product': deal_product
    }
    return render(request, 'store/deal-of-the-day.html', context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_item_qs = OrderItem.objects.filter(item=item, user=request.user, ordered=False)
    product = Product.objects.get(slug=slug)
    item_var = []  # item variation
    if request.method == 'POST':
        for items in request.POST:
            key = items
            val = request.POST[key]
            try:
                v = Variation.objects.get(
                    item=item,
                    category__iexact=key,
                    title__iexact=val
                )
                item_var.append(v)
            except:
                pass

        if len(item_var) > 0:
            # order_item_qs.variation.clear()
            for items in item_var:
                order_item_qs = order_item_qs.filter(
                    variation__exact=items,
                )
    if order_item_qs.exists():
        order_item = order_item_qs[0]
        get_product_stock_quantity = Product.objects.get(id=order_item.item.id)
        if order_item.quantity < get_product_stock_quantity.stock_quantity:
            quantity = request.POST.get('quantity')
            if quantity != None:
                if quantity:
                    order_item.quantity += int(quantity)
                else:
                    order_item.quantity = int(quantity)
            else:
                return redirect('product-detail', slug=slug)
            order_item.save()
        else:
            messages.info(request, "Stock Quantity Not avalable")
            return redirect("cart-summary")
    else:
        order_item = OrderItem.objects.create(
            item=item,
            user=request.user,
            ordered=False
        )
        quantity = request.POST.get('quantity')
        if quantity != None:
            order_item.quantity = int(quantity)
            order_item.variation.add(*item_var)
            order_item.save()
        else:
            return redirect('product-detail', slug=slug)

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if not order.items.filter(item__id=order_item.id).exists():
            order.items.add(order_item)
            messages.success(request, "Thank You successfully add")
            return redirect('product-detail', slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to cart.")
        return redirect('product-detail', slug=slug)


@login_required
def buy_now(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_item_qs = OrderItem.objects.filter(
        item=item, user=request.user, ordered=False)
    product = Product.objects.get(slug=slug)
    item_var = []  # item variation
    if request.method == 'POST':
        for items in request.POST:
            key = items
            val = request.POST[key]
            try:
                v = Variation.objects.get(
                    item=item,
                    category__iexact=key,
                    title__iexact=val
                )
                item_var.append(v)
            except:
                pass

        if len(item_var) > 0:
            # order_item_qs.variation.clear()
            for items in item_var:
                order_item_qs = order_item_qs.filter(
                    variation__exact=items,
                )
    if order_item_qs.exists():
        order_item = order_item_qs[0]
        get_product_stock_quantity = Product.objects.get(id=order_item.item.id)
        if order_item.quantity < get_product_stock_quantity.stock_quantity:
            quantity = request.POST.get('quantity')
            if quantity != None:
                if quantity:
                    order_item.quantity += int(quantity)
                else:
                    order_item.quantity = int(quantity)
            else:
                return redirect('address')
            order_item.save()
        else:
            messages.info(request, "Stock Quantity Not avalable")
            return redirect("address")
    else:
        order_item = OrderItem.objects.create(
            item=item,
            user=request.user,
            ordered=False
        )
        quantity = request.POST.get('quantity')
        if quantity != None:
            order_item.quantity = int(quantity)
            order_item.variation.add(*item_var)
            order_item.save()
        else:
            return redirect('address')

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if not order.items.filter(item__id=order_item.id).exists():
            order.items.add(order_item)
            messages.success(request, "Thank You successfully add")
            return redirect('address')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to cart.")
        return redirect('address')


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the cart
        if order.items.filter(item__slug=item.slug).exists():
            order_item = order.items.filter(item__slug=item.slug)[0]
            order_item.delete()
            messages.info(request, 'This item was removed from the cart.')
            return redirect('cart-summary')
        else:
            # the user does not have this item in the cart
            messages.info(request, 'This item was not in your cart.')
            return redirect('cart-summary')
    else:
        # the user does not have an active order
        messages.info(request, 'You do not have an active order.')
        return redirect('/')


@login_required
def CartSummary(request):
    try:
        # order_item = OrderItem.objects.filter(item.stock_quantity > 0)
        order = Order.objects.get(user=request.user, ordered=False)
        out_of_stock = any(item.item.stock_quantity <= 0 for item in order.items.all())
        form = CouponCodeForm(request.POST or None)
        context = {
            'order': order,
            'form': form,
            'out_of_stock': out_of_stock,
        }
        return render(request, 'store/cart_summary.html', context)

    except ObjectDoesNotExist:
        return redirect('/')


@login_required
def OrderSummary(request):
    try:
        order = Order.objects.filter(user=request.user, ordered=True)
        context = {
            'order': order,
        }
        return render(request, 'store/order_summary.html', context)

    except ObjectDoesNotExist:
        return redirect('/')


@login_required
def OrderDetails(request, pk):
    order = Order.objects.get(pk=pk)
    order_items = OrderItem.objects.filter(order=order)
    # order_parcel = ProductPercel.objects.get(order=order)
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'store/order_details.html', context)


@login_required
def render_order_pdf_view(request, *args, **kwargs):
    pk = kwargs.get('pk')
    order = get_object_or_404(Order, pk=pk)
    logo = WebsiteLogo.objects.all().first()
    template_path = 'store/order-report.html'
    context = {
        'order': order,
        'logo': logo,
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')

    # if download korte chai
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # if display korte chai
    response['Content-Disposition'] = 'filename="evazu-order-report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required
def Order_Item_Details(request, pk):
    try:
        cartitems = OrderItem.objects.get(
            pk=pk, user=request.user, ordered=True)
        # user_review = ProductReview.objects.filter(user=request.user,product=cartitems.item)
        form = ProductReviewForm(request.POST, request.FILES)
        if request.method == 'POST':
            form = ProductReviewForm(request.POST, request.FILES)
            if form.is_valid():
                form.instance.user = request.user
                form.instance.product = cartitems.item
                form.rating = request.POST.get('rating')
                form.image = request.POST.get('image')
                form.save()
                messages.success(request, "Successful Save")
                return redirect('order-summary')
            else:
                messages.error(request, 'Please correct the error below.')
        context = {
            'cartitems': cartitems,
            'form': form,
            # 'user_review':user_review
        }
        return render(request, 'store/order_item_details.html', context)
    except ObjectDoesNotExist:
        return redirect('/')


@method_decorator([login_required], name='dispatch')
class AddCouponView(View, LoginRequiredMixin):
    def post(self, *args, **kwargs):
        now = timezone.now()
        form = CouponCodeForm(self.request.POST or None)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            order = Order.objects.get(user=self.request.user, ordered=False)
            coupon = Coupon.objects.filter(code__iexact=code, valid_from__lte=now, valid_to__gte=now).exclude(
                order__user=self.request.user, max_value__lte=F('used')).first()
            if not coupon:
                messages.error(
                    self.request, 'You can\'t use same coupon again, or coupon does not exist')
                return redirect('cart-summary')
            else:
                try:
                    coupon.used += 1
                    coupon.save()
                    order.coupon = coupon
                    order.save()
                    messages.success(self.request, "Successfully added coupon")
                except:
                    messages.error(
                        self.request, "Max level exceeded for coupon")

                return redirect('cart-summary')


@method_decorator([login_required], name='dispatch')
class PrductQuantityIncrement(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        item = get_object_or_404(Product, slug=slug)
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                get_product_stock_quantity = Product.objects.get(
                    id=order_item.item.id)
                if order_item.quantity >= 1:
                    if order_item.quantity < get_product_stock_quantity.stock_quantity:
                        order_item.quantity += 1
                        order_item.save()
                        messages.info(
                            request, "This product quantity was update")
                        return redirect("cart-summary")
                    else:
                        messages.info(request, "Stock Quantity Not avalable")
                        return redirect("cart-summary")
            else:
                messages.info(request, "This item was not in your cart")
                return redirect("cart-summary", slug=slug)
        else:
            messages.info(request, "You do not have an active order")
            return redirect("cart-summary", slug=slug)


@method_decorator([login_required], name='dispatch')
class PrductQuantityDecrementr(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        item = get_object_or_404(Product, slug=slug)
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                    messages.info(request, "This product quantity was update")
                    return redirect("cart-summary")
                else:
                    order_item.delete()
                    messages.info(request, "This product delete from cart")
                return redirect("cart-summary")
            else:
                messages.info(request, "This item was not in your cart")
                return redirect("cart-summary", slug=slug)
        else:
            messages.info(request, "You do not have an active order")
            return redirect("cart-summary", slug=slug)

# WishList


@login_required
def add_to_wishlist(request, slug):
    products = get_object_or_404(Product, slug=slug)
    wish_product, created = WhishLIst.objects.get_or_create(
        wish_product=products, slug=products.slug, user=request.user)
    messages.info(request, "This Product add your wish list")
    return redirect('home')


@login_required
def wish_list(request):
    wish_product = WhishLIst.objects.filter(user=request.user)

    context = {
        'wish_product': wish_product
    }
    return render(request, 'store/wishlist.html', context)


@login_required
def delete_wish_list(request, slug):
    wish_product = WhishLIst.objects.filter(user=request.user, slug=slug)
    wish_product.delete()
    messages.info(request, "this product delete from your wish list")
    return redirect('wish-list')


@login_required
def profile_dashboard(request):
    order = Order.objects.filter(user=request.user, ordered=True).count()
    context = {
        'order': order,
    }
    return render(request, 'store/dashboard.html', context)


@login_required
def myreview(request):
    cartitems = OrderItem.objects.filter(
        user=request.user, ordered=True).order_by('-id')
    context = {
        'cartitems': cartitems,
    }
    return render(request, 'store/my-review.html', context)


@login_required
def review(request, pk):
    try:
        cartitems = OrderItem.objects.get(
            pk=pk, user=request.user, ordered=True)
        # user_review = ProductReview.objects.filter(user=request.user,product=cartitems.item)
        form = ProductReviewForm(request.POST, request.FILES)
        if request.method == 'POST':
            form = ProductReviewForm(request.POST, request.FILES)
            if form.is_valid():
                form.instance.user = request.user
                form.instance.product = cartitems.item
                form.rating = request.POST.get('rating')
                form.image = request.POST.get('image')
                form.save()
                messages.success(request, "Successful Save")
                return redirect('my-review')
            else:
                messages.error(request, 'Please correct the error below.')
        context = {
            'cartitems': cartitems,
            'form': form,
            # 'user_review':user_review
        }
        return render(request, 'store/review.html', context)
    except ObjectDoesNotExist:
        return redirect('/')


def contact_us(request):
    form = Contact_Form(request.POST)
    if request.method == 'POST':
        form = Contact_Form(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            phone = form.cleaned_data.get('phone')
            email = form.cleaned_data.get('email')
            subject = form.cleaned_data.get('subject')
            message = form.cleaned_data.get('message')

            submit = ConductData(
                name=name,
                phone=phone,
                email=email,
                subject=subject,
                message=message
            )
            submit.save()
            messages.success(request, 'Successfully Submit')
            return redirect('home')
    else:
        form = Contact_Form()
    context = {
        'form': form
    }
    return render(request, 'store/contact.html', context)


# Privacy Policy
# Terms and conditions
# Our Mission & Vision
# Returns Policy
# Shipping and Delivery

def privacy_policy(request):
    texts = PrivacyPolicy.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/privacy-policy.html', context)


def terms_conditions(request):
    texts = TermsAndConditions.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/terms-conditions.html', context)


def vision(request):
    texts = Vision.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/mission-vision.html', context)


def mission(request):
    texts = Mission.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/mission-vision.html', context)


def returns_policy(request):
    texts = Returns_Policy.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/returns-policy.html', context)


def shipping_delivery(request):
    texts = ShippingAndDelivery.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/shipping-delivery.html', context)


def about_us(request):
    texts = AboutUs.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/about-us.html', context)


def videogallery(request):
    videos = VideoGallery.objects.all()

    context = {
        'videos': videos
    }
    return render(request, 'store/videogallery.html', context)


def imagegallery(request):
    img = ImageGallery.objects.all()

    context = {
        'img': img
    }
    return render(request, 'store/imagegallery.html', context)
