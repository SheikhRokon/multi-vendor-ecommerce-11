
import requests
import json
from django.shortcuts import get_object_or_404, render, redirect
from requests import request
from store.models import *
from django.core.exceptions import ObjectDoesNotExist
from .forms import *
from django.views.generic import *
from django.contrib import messages
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect
from userapp.decorators import *
from userapp.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from userapp.forms import *
from django.views.generic.detail import DetailView
from django.contrib.auth import get_user_model
from other_vendors.models import VendorInformation
from other_vendors.forms import *

# Create your views here.


@login_required
@daseboard_required
def dashboard_home(request):
    user = request.user
    total_customer = User.objects.count()
    all_product_count = Product.objects.filter().count()
    vendor_product_count = Product.objects.filter(user=user).count()
    total_order = Order.objects.filter(ordered=True).count()
    my_product_order = Order.objects.filter(user=user, ordered=True).count()
    pending_order = Order.objects.filter(
        user=user, ordered=True, order_status='pending').count()
    processing_order = Order.objects.filter(
        user=user, ordered=True, order_status='processing').count()
    on_the_way_order = Order.objects.filter(
        user=user, ordered=True, order_status='on the way').count()
    complete_order = Order.objects.filter(
        user=user, ordered=True, order_status='complete').count()

    context = {
        'total_customer': total_customer,
        'all_product_count': all_product_count,
        'total_order': total_order,
        'my_product_order': my_product_order,
        'pending_order': pending_order,
        'processing_order': processing_order,
        'on_the_way_order': on_the_way_order,
        'complete_order': complete_order,
        'vendor_product_count': vendor_product_count,


    }
    return render(request, 'dashboard/index.html', context)


@login_required
@daseboard_required
def product_list(request):
    user = request.user
    User = get_user_model()
    if User.objects.filter(id=user.id).exists():
        products = Product.objects.filter(user=user)

    context = {
        'products': products,
    }
    return render(request, 'dashboard/product/product-list.html', context)


@login_required
@daseboard_required
def all_product_list(request):
    all_product = Product.objects.all()
    context = {
        'all_product': all_product,
    }
    return render(request, 'dashboard/product/all_product_list.html', context)


# product update

class ProductInline():
    form_class = ProductForm
    model = Product
    template_name = "dashboard/product/product-add.html"

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))

        form.instance.user = self.request.user
        self.object = form.save()

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            formset_save_func = getattr(
                self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('dashboard-product-list')

    def formset_variants_valid(self, formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        variants = formset.save(
            commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for variant in variants:
            variant.item = self.object
            variant.save()

    def formset_images_valid(self, formset):
        """
        Hook for custom formset saving. Useful if you have multiple formsets
        """
        images = formset.save(
            commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for image in images:
            image.product = self.object
            image.save()


class ProductCreate(ProductInline, CreateView):
    def get_context_data(self, **kwargs):
        ctx = super(ProductCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'variants': VariantFormSet(prefix='variants'),
                'images': ImageFormSet(prefix='images'),
            }
        else:
            return {
                'variants': VariantFormSet(self.request.POST or None, self.request.FILES or None, prefix='variants'),
                'images': ImageFormSet(self.request.POST or None, self.request.FILES or None, prefix='images'),
            }


class ProductUpdate(ProductInline, UpdateView):
    def get_context_data(self, **kwargs):
        ctx = super(ProductUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            'variants': VariantFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='variants'),
            'images': ImageFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='images'),
        }


@login_required
@daseboard_required
def delete_image(request, pk):
    try:
        image = ProductImgGallery.objects.get(id=pk)
    except Image.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
        )
        return redirect('update_product', pk=image.product.id)

    image.delete()
    messages.success(
        request, 'Image deleted successfully'
    )
    return redirect('product-update', pk=image.product.id)


@login_required
@daseboard_required
def delete_variant(request, pk):
    try:
        variant = Variation.objects.get(id=pk)
    except variant.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
        )
        return redirect('product-update', pk=variant.product.id)

    variant.delete()
    messages.success(
        request, 'Variant deleted successfully'
    )
    return redirect('product-update', pk=variant.item.id)


@login_required
@daseboard_required
def product_delete(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Successfully delete your post')
        return redirect('dashboard-product-list')
    return render(request, 'dashboard/product/delete.html')


# Category pART SRART

@login_required
@daseboard_required
def category_list(request):
    categories = ProductCategory.objects.all()

    context = {
        'categories': categories
    }
    return render(request, 'dashboard/category/categorie-list.html', context)


def inactive_category_list(request):
    categories = ProductCategory.objects.filter(show_status=False)

    context = {
        'categories': categories
    }
    return render(request, 'daseboard/cetegory/inactivecategorielist.html', context)


@login_required
@daseboard_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add your new category')
            return redirect('category-list')
    else:
        form = CategoryAddForm()
    return render(request, 'dashboard/category/categorie-add.html', {'form': form})


@login_required
@daseboard_required
def category_update(request, slug):
    category = get_object_or_404(ProductCategory, slug=slug)
    form = CategoryAddForm(request.POST, request.FILES, instance=category)

    if request.method == 'POST':
        form = CategoryAddForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.img = request.POST.get('img')
            form.save()
            messages.success(request, 'Successfully update Category')
            return redirect('category-list')
    else:
        form = CategoryAddForm(instance=category)
    context = {
        'category': category,
        'form': form,
    }
    return render(request, 'dashboard/category/categorie-add.html', context)


@login_required
@daseboard_required
def category_delete(request, slug):
    category = ProductCategory.objects.get(slug=slug)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Successfully delete your post')
        return redirect('category-list')
    return render(request, 'dashboard/category/categorie-delete.html', {'category': category})


# brand part start
@login_required
@daseboard_required
def brand_list(request):
    brands = Brand.objects.all()

    context = {
        'brands': brands
    }
    return render(request, 'dashboard/brand/brand-list.html', context)


def inactive_brand_list(request):
    brands = Brand.objects.filter(show_status=False)

    context = {
        'brands': brands
    }
    return render(request, 'daseboard/brand/inactive-brand-list.html', context)


@login_required
@daseboard_required
def brand_add(request):
    if request.method == 'POST':
        form = BrandAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add your new brand')
            return redirect('brand-list')
    else:
        form = BrandAddForm()
    return render(request, 'dashboard/brand/brand-add.html', {'form': form})


@login_required
@daseboard_required
def brand_update(request, slug):
    brands = Brand.objects.get(slug=slug)
    form = BrandAddForm(request.POST, request.FILES, instance=brands)

    if request.method == 'POST':
        form = BrandAddForm(request.POST, request.FILES, instance=brands)
        if form.is_valid():
            form.image = request.POST.get('image')
            form.save()
            messages.success(request, 'Successfully update Category')
            return redirect('brand-list')
    else:
        form = BrandAddForm(instance=brands)
    context = {
        'brands': brands,
        'form': form,
    }
    return render(request, 'dashboard/brand/brand-add.html', context)


@login_required
@daseboard_required
def brand_delete(request, slug):
    brand = Brand.objects.get(slug=slug)
    if request.method == 'POST':
        brand.delete()
        messages.success(request, 'Successfully delete your post')
        return redirect('brand-list')
    return render(request, 'dashboard/brand/brand-delete.html', {'brand': brand})

# banner


@login_required
@daseboard_required
def banner_list(request):
    banner = Banner.objects.all()

    context = {
        'banner': banner
    }
    return render(request, 'dashboard/banner/banner-list.html', context)


@login_required
@daseboard_required
def banner_add(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add your new banner')
            return redirect('banner-list')
    else:
        form = BannerForm()
    return render(request, 'dashboard/banner/banner-add.html', {'form': form})


@login_required
@daseboard_required
def banner_update(request, pk):
    banner = Banner.objects.get(pk=pk)
    form = BannerForm(request.POST, request.FILES, instance=banner)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update banner')
            return redirect('banner-list')
    else:
        form = BannerForm(instance=banner)
    context = {
        'banner': banner,
        'form': form,
    }
    return render(request, 'dashboard/banner/banner-add.html', context)


@login_required
@daseboard_required
def banner_delete(request, pk):
    banner = Banner.objects.get(pk=pk)
    if request.method == 'POST':
        banner.delete()
        messages.success(request, 'Successfully delete your post')
        return redirect('banner-list')
    return render(request, 'dashboard/banner/banner-delete.html', {'banner': banner})


# logo

@login_required
@daseboard_required
def logo_list(request):
    logo = WebsiteLogo.objects.all()
    context = {
        'logo': logo
    }
    return render(request, 'dashboard/logo/logo-list.html', context)


@login_required
@daseboard_required
def logo_add(request):
    if request.method == 'POST':
        form = LogoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add your new logo')
            return redirect('logo-list')
    else:
        form = LogoForm()
    return render(request, 'dashboard/logo/logo-add.html', {'form': form})


@login_required
@daseboard_required
def logo_update(request, pk):
    logo = WebsiteLogo.objects.get(pk=pk)
    form = LogoForm(request.POST, request.FILES, instance=logo)
    if request.method == 'POST':
        form = LogoForm(request.POST, request.FILES, instance=logo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update logo')
            return redirect('logo-list')
    else:
        form = LogoForm(instance=logo)
    context = {
        'logo': logo,
        'form': form,
    }
    return render(request, 'dashboard/logo/logo-add.html', context)


@login_required
@daseboard_required
def logo_delete(request, pk):
    logo = WebsiteLogo.objects.get(pk=pk)
    if request.method == 'POST':
        logo.delete()
        messages.success(request, 'Successfully delete your post')
        return redirect('logo-list')
    return render(request, 'dashboard/logo/logo-delete.html', {'logo': logo})

# start coupon part


@login_required
@daseboard_required
def coupon_list(request):
    coupons = Coupon.objects.all()

    context = {
        'coupons': coupons
    }
    return render(request, 'dashboard/coupon/coupon-list.html', context)


@login_required
@daseboard_required
def coupon_add(request):
    if request.method == 'POST':
        form = CouponAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(request, 'successfully add  new Coupon')
            return redirect('coupon-list')
    else:
        form = CouponAddForm()
    return render(request, 'dashboard/coupon/coupon-add.html', {'form': form})


@login_required
@daseboard_required
def coupon_update(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    form = CouponAddForm(request.POST, request.FILES, instance=coupon)
    if request.method == 'POST':
        form = CouponAddForm(request.POST, request.FILES, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update coupon')
            return redirect('coupon-list')
    else:
        form = CouponAddForm(instance=coupon)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/coupon/coupon-add.html', context)


@login_required
@daseboard_required
def coupon_delete(request, pk):
    coupon = Coupon.objects.get(pk=pk)
    if request.method == 'POST':
        coupon.delete()
        messages.success(request, 'Successfully delete')
        return redirect('coupon-list')
    return render(request, 'dashboard/coupon/coupon-delete.html', {'coupon': coupon})


# start flashsale part
@login_required
@daseboard_required
def flashsale_list(request):
    flashsale = FlashSale.objects.all()

    context = {
        'flashsale': flashsale
    }
    return render(request, 'dashboard/flashsale/flashsale-list.html', context)


@login_required
@daseboard_required
def flashsale_add(request):
    if request.method == 'POST':
        form = FlashsaleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add  new flashsale')
            return redirect('flashsale-list')
    else:
        form = FlashsaleForm()
    return render(request, 'dashboard/flashsale/flashsale-add.html', {'form': form})


@login_required
@daseboard_required
def flashsale_update(request, pk):
    flashsale = get_object_or_404(FlashSale, pk=pk)
    form = FlashsaleForm(request.POST, instance=flashsale)
    if request.method == 'POST':
        form = FlashsaleForm(request.POST, instance=flashsale)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update flashsale')
            return redirect('flashsale-list')
    else:
        form = FlashsaleForm(instance=flashsale)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/flashsale/flashsale-add.html', context)


@login_required
@daseboard_required
def flashsale_delete(request, pk):
    flashsale = FlashSale.objects.get(pk=pk)
    if request.method == 'POST':
        flashsale.delete()
        messages.success(request, 'Successfully delete')
        return redirect('flashsale-list')
    return render(request, 'dashboard/flashsale/flashsale-delete.html', {'flashsale': flashsale})


@login_required
@daseboard_required
def campaign_category_list(request):
    campaign_category = Campaign.objects.all()

    context = {
        'campaign_category': campaign_category
    }
    return render(request, 'dashboard/campaign-category/campaign-category-list.html', context)


@login_required
@daseboard_required
def campaign_category_add(request):
    if request.method == 'POST':
        form = CampaignCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('campaign-category-list')
    else:
        form = CampaignCategoryForm()
    return render(request, 'dashboard/campaign-category/campaign-category-add.html', {'form': form})


@login_required
@daseboard_required
def campaign_category_update(request, pk):
    campaign_category = get_object_or_404(Campaign, pk=pk)
    form = CampaignCategoryForm(request.POST, instance=campaign_category)
    if request.method == 'POST':
        form = CampaignCategoryForm(request.POST, instance=campaign_category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully')
            return redirect('campaign-category-list')
    else:
        form = CampaignCategoryForm(instance=campaign_category)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/campaign-category/campaign-category-add.html', context)


@login_required
@daseboard_required
def campaign_category_delete(request, pk):
    campaign_category = Campaign.objects.get(pk=pk)
    if request.method == 'POST':
        campaign_category.delete()
        messages.success(request, 'Successfully delete')
        return redirect('campaign-category-list')
    return render(request, 'dashboard/campaign-category/campaign-category-delete.html', {'campaign_category': campaign_category})


# start campaign-product part
@login_required
@daseboard_required
def campaign_product_list(request):
    campaign_product = CampaignProduct.objects.all()

    context = {
        'campaign_product': campaign_product
    }
    return render(request, 'dashboard/campaign-product/campaign-product-list.html', context)


@login_required
@daseboard_required
def campaign_product_add(request):
    if request.method == 'POST':
        form = CampaignProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('campaign-product-list')
    else:
        form = CampaignProductForm()
    return render(request, 'dashboard/campaign-product/campaign-product-add.html', {'form': form})


@login_required
@daseboard_required
def campaign_product_update(request, pk):
    campaign_product = get_object_or_404(CampaignProduct, pk=pk)
    form = CampaignProductForm(request.POST, instance=campaign_product)
    if request.method == 'POST':
        form = CampaignProductForm(request.POST, instance=campaign_product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update')
            return redirect('campaign-product-list')
    else:
        form = CampaignProductForm(instance=campaign_product)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/campaign-product/campaign-product-add.html', context)


@login_required
@daseboard_required
def campaign_product_delete(request, pk):
    campaign_product = CampaignProduct.objects.get(pk=pk)
    if request.method == 'POST':
        campaign_product.delete()
        messages.success(request, 'Successfully delete')
        return redirect('campaign-product-list')
    return render(request, 'dashboard/campaign-product/campaign-product-delete.html', {'campaign_product': campaign_product})


# start deal-of-the-day-product part
@login_required
@daseboard_required
def deal_of_the_day_product_list(request):
    deal_of_the_day = DealOfTheDayProduct.objects.all()

    context = {
        'deal_of_the_day': deal_of_the_day
    }
    return render(request, 'dashboard/deal_of-the_day/dotd_product-list.html', context)


@login_required
@daseboard_required
def deal_of_the_day_product_add(request):
    if request.method == 'POST':
        form = DealOfTheDayProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('deal_of_the_day_product-list')
    else:
        form = DealOfTheDayProductForm()
    return render(request, 'dashboard/deal_of-the_day/dotd_product-add.html', {'form': form})


@login_required
@daseboard_required
def deal_of_the_day_product_update(request, pk):
    deal_of_the_day = get_object_or_404(DealOfTheDayProduct, pk=pk)
    form = DealOfTheDayProductForm(request.POST, instance=deal_of_the_day)
    if request.method == 'POST':
        form = DealOfTheDayProductForm(request.POST, instance=deal_of_the_day)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update')
            return redirect('deal_of_the_day_product-list')
    else:
        form = DealOfTheDayProductForm(instance=deal_of_the_day)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/deal_of-the_day/dotd_product-add.html', context)


@login_required
@daseboard_required
def deal_of_the_day_product_delete(request, pk):
    deal_of_the_day = DealOfTheDayProduct.objects.get(pk=pk)
    if request.method == 'POST':
        deal_of_the_day.delete()
        messages.success(request, 'Successfully delete')
        return redirect('deal_of_the_day_product-list')
    return render(request, 'dashboard/deal_of-the_day/dotd_product-delete.html', {'deal_of_the_day': deal_of_the_day})


# start deal-of-the-day-product part
@login_required
@daseboard_required
def rating_list(request):
    rating = ProductReview.objects.all()
    context = {
        'rating': rating
    }
    return render(request, 'dashboard/rating/rating-list.html', context)


@login_required
@daseboard_required
def rating_add(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('rating-list')
    else:
        form = ReviewForm()
    return render(request, 'dashboard/rating/rating-add.html', {'form': form})


@login_required
@daseboard_required
def rating_update(request, pk):
    rating = get_object_or_404(ProductReview, pk=pk)
    form = ReviewForm(request.POST, instance=rating)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update')
            return redirect('rating-list')
    else:
        form = ReviewForm(instance=rating)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/rating/rating-add.html', context)


@login_required
@daseboard_required
def rating_delete(request, pk):
    rating = ProductReview.objects.get(pk=pk)
    if request.method == 'POST':
        rating.delete()
        messages.success(request, 'Successfully delete')
        return redirect('rating-list')
    return render(request, 'dashboard/rating/rating-delete.html', {'rating': rating})


# Contact
@login_required
@daseboard_required
def contact_data_list(request):
    contact_datas = ConductData.objects.all()

    context = {
        'contact_datas': contact_datas
    }
    return render(request, 'dashboard/contact/contact-list.html', context)


@login_required
@daseboard_required
def contact_data_detail(request, pk):
    contact_datas = ConductData.objects.get(pk=pk)
    contact_datas.view_status = True
    contact_datas.save()
    context = {
        'contact_datas': contact_datas
    }
    return render(request, 'dashboard/contact/contact-detail.html', context)


@login_required
@daseboard_required
def contact_add(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('contact-list')
    else:
        form = ContactForm()
    return render(request, 'dashboard/contact/contact-add.html', {'form': form})


@login_required
@daseboard_required
def contact_update(request, pk):
    contact = get_object_or_404(ConductData, pk=pk)
    form = ContactForm(request.POST, instance=contact)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update')
            return redirect('contact-list')
    else:
        form = ContactForm(instance=contact)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/contact/contact-add.html', context)


@login_required
@daseboard_required
def contact_delete(request, pk):
    contact = ConductData.objects.get(pk=pk)
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Successfully delete')
        return redirect('contact-list')
    return render(request, 'dashboard/contact/contact-delete.html', {'contact': contact})


# Privacy Policy
@login_required
@daseboard_required
def privacy_policy_list(request):
    privacy_policy = PrivacyPolicy.objects.all()

    context = {
        'privacy_policy': privacy_policy
    }
    return render(request, 'dashboard/privacy-policy/privacy_policy-list.html', context)


@login_required
@daseboard_required
def privacy_policy_add(request):
    if request.method == 'POST':
        form = PrivacyPolicyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('privacy_policy-list')
    else:
        form = PrivacyPolicyForm()
    return render(request, 'dashboard/privacy-policy/privacy_policy-add.html', {'form': form})


@login_required
@daseboard_required
def privacy_policy_update(request, pk):
    privacy_policy = get_object_or_404(PrivacyPolicy, pk=pk)
    form = PrivacyPolicyForm(request.POST, instance=privacy_policy)
    if request.method == 'POST':
        form = PrivacyPolicyForm(request.POST, instance=privacy_policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update')
            return redirect('privacy_policy-list')
    else:
        form = PrivacyPolicyForm(instance=privacy_policy)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/privacy-policy/privacy_policy-add.html', context)


def privacy_policy_delete(request, pk):
    privacy_policy = PrivacyPolicy.objects.get(pk=pk)
    if request.method == 'POST':
        privacy_policy.delete()
        messages.success(request, 'Successfully delete')
        return redirect('privacy_policy-list')
    return render(request, 'dashboard/privacy-policy/privacy_policy-delete.html', {'privacy_policy': privacy_policy})


# Terms Condition
@login_required
@daseboard_required
def terms_condition_list(request):
    terms_condition = TermsAndConditions.objects.all()

    context = {
        'terms_condition': terms_condition
    }
    return render(request, 'dashboard/terms-condition/terms_condition-list.html', context)


@login_required
@daseboard_required
def terms_condition_add(request):
    if request.method == 'POST':
        form = TermsAndConditionsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('terms_condition-list')
    else:
        form = TermsAndConditionsForm()
    return render(request, 'dashboard/terms-condition/terms_condition-add.html', {'form': form})


@login_required
@daseboard_required
def terms_condition_update(request, pk):
    terms_condition = get_object_or_404(TermsAndConditions, pk=pk)
    form = TermsAndConditionsForm(request.POST, instance=terms_condition)
    if request.method == 'POST':
        form = TermsAndConditionsForm(request.POST, instance=terms_condition)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update')
            return redirect('terms_condition-list')
    else:
        form = TermsAndConditionsForm(instance=terms_condition)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/terms-condition/terms_condition-add.html', context)


@login_required
@daseboard_required
def terms_condition_delete(request, pk):
    terms_condition = TermsAndConditions.objects.get(pk=pk)
    if request.method == 'POST':
        terms_condition.delete()
        messages.success(request, 'Successfully delete')
        return redirect('terms_condition-list')
    return render(request, 'dashboard/terms-condition/terms_condition-delete.html', {'terms_condition': terms_condition})


# mission
@login_required
@daseboard_required
def mission_list(request):
    mission = Mission.objects.all()

    context = {
        'mission': mission
    }
    return render(request, 'dashboard/mission/mission-list.html', context)


@login_required
@daseboard_required
def mission_add(request):
    if request.method == 'POST':
        form = MissionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('mission-list')
    else:
        form = MissionForm()
    return render(request, 'dashboard/mission/mission-add.html', {'form': form})


@login_required
@daseboard_required
def mission_update(request, pk):
    mission = get_object_or_404(Mission, pk=pk)
    form = MissionForm(request.POST, instance=mission)
    if request.method == 'POST':
        form = MissionForm(request.POST, instance=mission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update')
            return redirect('mission-list')
    else:
        form = MissionForm(instance=mission)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/mission/mission-add.html', context)


@login_required
@daseboard_required
def mission_delete(request, pk):
    mission = Mission.objects.get(pk=pk)
    if request.method == 'POST':
        mission.delete()
        messages.success(request, 'Successfully delete')
        return redirect('mission-list')
    return render(request, 'dashboard/mission/mission-delete.html', {'mission': mission})


# vision
@login_required
@daseboard_required
def vision_list(request):
    vision = Vision.objects.all()

    context = {
        'vision': vision
    }
    return render(request, 'dashboard/vision/vision-list.html', context)


@login_required
@daseboard_required
def vision_add(request):
    if request.method == 'POST':
        form = VisionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('vision-list')
    else:
        form = VisionForm()
    return render(request, 'dashboard/vision/vision-add.html', {'form': form})


@login_required
@daseboard_required
def vision_update(request, pk):
    vision = get_object_or_404(Vision, pk=pk)
    form = VisionForm(request.POST, instance=vision)
    if request.method == 'POST':
        form = VisionForm(request.POST, instance=vision)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update')
            return redirect('vision-list')
    else:
        form = VisionForm(instance=vision)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/vision/vision-add.html', context)


@login_required
@daseboard_required
def vision_delete(request, pk):
    vision = Vision.objects.get(pk=pk)
    if request.method == 'POST':
        vision.delete()
        messages.success(request, 'Successfully delete')
        return redirect('vision-list')
    return render(request, 'dashboard/vision/vision-delete.html', {'vision': vision})


# returns_policy
@login_required
@daseboard_required
def returns_policy_list(request):
    returns_policy = Returns_Policy.objects.all()

    context = {
        'returns_policy': returns_policy
    }
    return render(request, 'dashboard/returns_policy/returns_policy-list.html', context)


@login_required
@daseboard_required
def returns_policy_add(request):
    if request.method == 'POST':
        form = Returns_PolicyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('returns_policy-list')
    else:
        form = Returns_PolicyForm()
    return render(request, 'dashboard/returns_policy/returns_policy-add.html', {'form': form})


@login_required
@daseboard_required
def returns_policy_update(request, pk):
    returns_policy = get_object_or_404(Returns_Policy, pk=pk)
    form = Returns_PolicyForm(request.POST, instance=returns_policy)
    if request.method == 'POST':
        form = Returns_PolicyForm(request.POST, instance=returns_policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update')
            return redirect('returns_policy-list')
    else:
        form = Returns_PolicyForm(instance=returns_policy)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/returns_policy/returns_policy-add.html', context)


@login_required
@daseboard_required
def returns_policy_delete(request, pk):
    returns_policy = Returns_Policy.objects.get(pk=pk)
    if request.method == 'POST':
        returns_policy.delete()
        messages.success(request, 'Successfully delete')
        return redirect('returns_policy-list')
    return render(request, 'dashboard/returns_policy/returns_policy-delete.html', {'returns_policy': returns_policy})


# shipping_delivery
@login_required
@daseboard_required
def shipping_delivery_list(request):
    shipping_delivery = ShippingAndDelivery.objects.all()

    context = {
        'shipping_delivery': shipping_delivery
    }
    return render(request, 'dashboard/shipping_delivery/shipping_delivery-list.html', context)


@login_required
@daseboard_required
def shipping_delivery_add(request):
    if request.method == 'POST':
        form = ShippingAndDeliveryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('shipping_delivery-list')
    else:
        form = ShippingAndDeliveryForm()
    return render(request, 'dashboard/shipping_delivery/shipping_delivery-add.html', {'form': form})


@login_required
@daseboard_required
def shipping_delivery_update(request, pk):
    shipping_delivery = get_object_or_404(ShippingAndDelivery, pk=pk)
    form = ShippingAndDeliveryForm(request.POST, instance=shipping_delivery)
    if request.method == 'POST':
        form = ShippingAndDeliveryForm(
            request.POST, instance=shipping_delivery)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update')
            return redirect('shipping_delivery-list')
    else:
        form = ShippingAndDeliveryForm(instance=shipping_delivery)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/returns_policy/shipping_delivery-add.html', context)


@login_required
@daseboard_required
def shipping_delivery_delete(request, pk):
    shipping_delivery = ShippingAndDelivery.objects.get(pk=pk)
    if request.method == 'POST':
        shipping_delivery.delete()
        messages.success(request, 'Successfully delete')
        return redirect('shipping_delivery-list')
    return render(request, 'dashboard/shipping_delivery/shipping_delivery-delete.html', {'shipping_delivery': shipping_delivery})


# aboutus
@login_required
@daseboard_required
def aboutus_list(request):
    aboutus = AboutUs.objects.all()

    context = {
        'aboutus': aboutus
    }
    return render(request, 'dashboard/aboutus/aboutus-list.html', context)


@login_required
@daseboard_required
def aboutus_add(request):
    if request.method == 'POST':
        form = AboutUsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('aboutus-list')
    else:
        form = AboutUsForm()
    return render(request, 'dashboard/aboutus/aboutus-add.html', {'form': form})


@login_required
@daseboard_required
def aboutus_update(request, pk):
    aboutus = get_object_or_404(AboutUs, pk=pk)
    form = AboutUsForm(request.POST, instance=aboutus)
    if request.method == 'POST':
        form = AboutUsForm(request.POST, instance=aboutus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update')
            return redirect('aboutus-list')
    else:
        form = AboutUsForm(instance=aboutus)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/returns_policy/aboutus-add.html', context)


@login_required
@daseboard_required
def aboutus_delete(request, pk):
    aboutus = AboutUs.objects.get(pk=pk)
    if request.method == 'POST':
        aboutus.delete()
        messages.success(request, 'Successfully delete')
        return redirect('aboutus-list')
    return render(request, 'dashboard/aboutus/aboutus-delete.html', {'aboutus': aboutus})


@login_required
@daseboard_required
def all_order(request):
    try:
        user = request.user
        order_vendor = Order.objects.filter(
            user=user, ordered=True).order_by('-id')  # Order vendor
        order = Order.objects.filter(ordered=True).order_by(
            '-id')  # Superadmin order
        context = {
            'order_vendor': order_vendor,
            'order': order,
        }
        return render(request, 'dashboard/order/order-list.html', context)

    except ObjectDoesNotExist:
        pass


@login_required
@daseboard_required
def all_order_list(request):
    try:
        order = Order.objects.filter(ordered=True).order_by(
            '-id')  # Superadmin order
        context = {
            'order': order,
        }
        return render(request, 'dashboard/order/all_order_list.html', context)

    except ObjectDoesNotExist:
        pass


@login_required
@daseboard_required
def all_OrderDetails(request, pk):
    order = Order.objects.get(pk=pk)
    order.order_read_status = True
    order.save()

    order_items = OrderItem.objects.filter(order=order)
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'dashboard/order/all_order_details.html', context)


@login_required
@daseboard_required
def OrderDetails(request, pk):
    user = request.user
    order = get_object_or_404(Order, user=user, pk=pk)
    order.order_read_status = True
    order.save()

    order_items_vendor = OrderItem.objects.filter(order=order)
    context = {
        'order': order,
        'order_items_vendor': order_items_vendor,
    }
    return render(request, 'dashboard/order/order-details.html', context)


@login_required
@daseboard_required
def order_update(request, pk):
    order = Order.objects.get(pk=pk)
    form = OrderupdateForm(request.POST, request.FILES, instance=order)

    if request.method == 'POST':
        form = OrderupdateForm(request.POST, request.FILES, instance=order)
        if form.is_valid():
            form.image = request.POST.get('image')
            form.save()
            messages.success(request, 'Successfully update order')
            return redirect('all-order')
    else:
        form = OrderupdateForm(instance=order)
    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'dashboard/order/order-update.html', context)


@login_required
@daseboard_required
def shipping_address_update(request, pk):
    order = Order.objects.get(pk=pk)
    shipping_address = ShipingAddress.objects.get(order=order)
    form = OrderShippingAddressUpdateForm(
        request.POST, request.FILES, instance=shipping_address)

    if request.method == 'POST':
        form = OrderShippingAddressUpdateForm(
            request.POST, request.FILES, instance=shipping_address)
        if form.is_valid():
            form.image = request.POST.get('image')
            form.save()
            messages.success(request, 'Successfully update order')
            return redirect('all-order')
    else:
        form = OrderShippingAddressUpdateForm(instance=shipping_address)
    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'dashboard/order/shipping-address-update.html', context)


# User

@login_required
@daseboard_required
def user_list(request):
    user = User.objects.all()
    context = {
        'user': user
    }
    return render(request, 'dashboard/user/user-list.html', context)


@login_required
@daseboard_required
def user_add(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('user-list')
    else:
        form = RegisterForm()
    return render(request, 'dashboard/user/user-add.html', {'form': form})


@login_required
@daseboard_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST, instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update')
            return redirect('user-list')
    else:
        form = UserForm(instance=user)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/user/user-add.html', context)


@login_required
@daseboard_required
def user_delete(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Successfully delete')
        return redirect('user-list')
    return render(request, 'dashboard/user/user-delete.html', {'user': user})


@login_required
@daseboard_required
def profile_list(request):
    profile = Profile.objects.all()
    context = {
        'profile': profile
    }
    return render(request, 'dashboard/profile/profile-list.html', context)


@login_required
@daseboard_required
def profile_add(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add')
            return redirect('profile-list')
    else:
        form = UpdateProfileForm()
    return render(request, 'dashboard/profile/profile-add.html', {'form': form})


@login_required
@daseboard_required
def profile_update(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    form = UpdateProfileForm(request.POST, instance=profile)
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update')
            return redirect('profile-list')
    else:
        form = UpdateProfileForm(instance=profile)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/profile/profile-add.html', context)


@login_required
@daseboard_required
def profile_delete(request, pk):
    profile = Profile.objects.get(pk=pk)
    if request.method == 'POST':
        profile.delete()
        messages.success(request, 'Successfully delete')
        return redirect('profile-list')
    return render(request, 'dashboard/profile/profile-delete.html', {'profile': profile})


@login_required
@daseboard_required
def create_redx_parcel(request, pk):
    order = Order.objects.get(pk=pk)
    form = PercelForm(request.POST)
    if request.method == 'POST':
        form = PercelForm(request.POST)
        if form.is_valid():
            form.instance.order = order
            form.instance.customer_name = order.shipping_address.full_name
            form.instance.customer_phone = order.shipping_address.phone
            form.instance.customer_address = order.shipping_address.full_address
            form.instance.merchant_invoice_id = order.id
            form.instance.cash_collection_amount = order.due_amount

            token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4MDYyNzMiLCJpYXQiOjE2NjM1Nzg3MTEsImlzcyI6IkRHUG9RTzZnRGxXaFdOaTNqRGVxNk9nRkdzSGVlWkd4Iiwic2hvcF9pZCI6ODA2MjczLCJ1c2VyX2lkIjoxNTE1NDU3fQ.1LKrqQ6gX7HPOh5QxPCpOGERoIgNNXzkLQoilgg3_eg'
            api_url = 'https://sandbox.redx.com.bd/v1.0.0-beta/parcel'

            payload = json.dumps({
                "customer_name": order.shipping_address.full_name,
                "customer_phone":  order.shipping_address.phone,
                "delivery_area":  request.POST.get('delivery_area'),
                "delivery_area_id": 1,
                "customer_address":  order.shipping_address.full_address,
                "merchant_invoice_id": str(order.id),
                "cash_collection_amount":  order.due_amount,
                "parcel_weight":  request.POST.get('parcel_weight'),
            })
            headers = {
                "Content-Type": "application/json",
                'API-ACCESS-TOKEN':  f'Bearer {token}'
            }
            response = requests.request(
                "POST", api_url, headers=headers, data=payload)
            print(response.text)

            resp = json.loads(response.text)

            for x in resp:
                form.instance.tracking_id = resp[x]

            form.save()
            order.redx_percel_traking_number = form.instance.tracking_id
            order.save()

            return redirect('all-order')
    else:
        form = PercelForm()
        return render(request, 'dashboard/order_parcel/redx-percel-create.html', {'form': form, 'order': order})


@login_required
@daseboard_required
def image_list(request):
    images = ImageGallery.objects.all()

    context = {
        'images': images
    }
    return render(request, 'daseboard/gallery/image-list.html', context)


@login_required
@daseboard_required
def image_add(request):
    if request.method == 'POST':
        form = ImageAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add  new image')
            return redirect('image-list')
    else:
        form = ImageAddForm()
    return render(request, 'daseboard/gallery/image-add.html', {'form': form})


@login_required
@daseboard_required
def image_update(request, pk):
    images = ImageGallery.objects.get(pk=pk)
    form = ImageAddForm(request.POST, request.FILES, instance=images)

    if request.method == 'POST':
        form = ImageAddForm(request.POST, request.FILES, instance=images)
        if form.is_valid():
            form.image = request.POST.get('image')
            form.save()
            messages.success(request, 'Successfully update Category')
            return redirect('image-list')
    else:
        form = ImageAddForm(instance=images)
    context = {
        'images': images,
        'form': form,
    }
    return render(request, 'daseboard/gallery/image-update.html', context)


def image_delete(request, pk):
    image = ImageGallery.objects.get(pk=pk)
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Successfully delete your post')
        return redirect('image-list')
    return render(request, 'daseboard/delete.html')


@login_required
@daseboard_required
def video_list(request):
    videos = VideoGallery.objects.all()

    context = {
        'videos': videos
    }
    return render(request, 'daseboard/gallery/video-list.html', context)


@login_required
@daseboard_required
def video_add(request):
    if request.method == 'POST':
        form = VideoAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully add  new video')
            return redirect('video-list')
    else:
        form = VideoAddForm()
    return render(request, 'daseboard/gallery/video-add.html', {'form': form})


@login_required
@daseboard_required
def video_update(request, pk):
    video = VideoGallery.objects.get(pk=pk)
    form = VideoAddForm(request.POST, request.FILES, instance=video)

    if request.method == 'POST':
        form = VideoAddForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully update ')
            return redirect('video-list')
    else:
        form = VideoAddForm(instance=video)
    context = {
        'video': video,
        'form': form,
    }
    return render(request, 'daseboard/gallery/video-update.html', context)


def video_delete(request, pk):
    video = VideoGallery.objects.get(pk=pk)
    if request.method == 'POST':
        video.delete()
        messages.success(request, 'Successfully delete your post')
        return redirect('video-list')
    return render(request, 'daseboard/delete.html')


# vendor_profile_list
@login_required
@daseboard_required
def profile_accept_list(request):
    vendor_profile = VendorInformation.objects.filter(is_verified=True)

    context = {
        'vendor_profile': vendor_profile,
    }
    return render(request, 'dashboard/vendor-profile/profile_accept_list.html', context)


@login_required
@daseboard_required
def profile_unaccept_list(request):
    vendor_profile = VendorInformation.objects.filter(is_verified=False)

    context = {
        'vendor_profile': vendor_profile,
    }
    return render(request, 'dashboard/vendor-profile/profile_unaccept_list.html', context)


@login_required
@daseboard_required
def vendor_profile_update(request, pk):
    profile = get_object_or_404(VendorInformation, pk=pk)
    if request.method == 'POST':
        form = VendorInformationFormUpdate(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated')
            # Assuming you have defined this URL name
            return redirect('profile_accept_list')
    else:
        form = VendorInformationFormUpdate(instance=profile)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/vendor-profile/profile_update.html', context)


@login_required
@daseboard_required
def vendor_profile_delete(request, pk):
    profile = VendorInformation.objects.get(pk=pk)
    if request.method == 'POST':
        profile.delete()
        messages.success(request, 'Successfully delete')
        return redirect('vendor_profile_list')
    return render(request, 'dashboard/vendor-profile/profile-delete.html', {'profile': profile})
