from webbrowser import register
from django.contrib import admin
from .models import *
# Register your models here.
class ProductImgGalleryAdmin(admin.StackedInline):
    model = ProductImgGallery
    min_num = 0
    extra = 1

class ProductVriationAdmin(admin.StackedInline):
    model = Variation
    min_num = 0
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImgGalleryAdmin,ProductVriationAdmin]
 

admin.site.register(ProductCategory)
admin.site.register(Product, ProductAdmin)
admin.site.register(Banner)
admin.site.register(Brand)
admin.site.register(Variation)
admin.site.register(OrderItem)
admin.site.register(ProductReview)
admin.site.register(Order)
admin.site.register(Coupon)
admin.site.register(WhishLIst)
admin.site.register(VideoGallery)
admin.site.register(ImageGallery)
admin.site.register(ConductData)
admin.site.register(FlashSale)
admin.site.register(Campaign)
admin.site.register(CampaignProduct)
admin.site.register(DealOfTheDayProduct)
admin.site.register(WebsiteLogo)
admin.site.register(PriceRange)
admin.site.register(PrivacyPolicy)
admin.site.register(TermsAndConditions)
admin.site.register(Returns_Policy)
admin.site.register(ShippingAndDelivery)
admin.site.register(ProductPercel)

