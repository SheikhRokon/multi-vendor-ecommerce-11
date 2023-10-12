from django.urls import path
from .views import *



urlpatterns =[
    path('',ProductView.as_view(), name='home'),
    path('product/detail/<slug>/', ProductDetail.as_view(), name='product-detail'),
    path('products/category/<slug>/', ProductCategoryFiltering.as_view(), name='category'),
    path('products/brand/<slug>/', brandfiltering, name='brand'),
    path('allproduct/shop/', shop, name='shop'),
    path('FlashSale/Product/', flash_sale, name='flash-sale'),
    path('deal-of-the-day/Product/', deal_of_the_day, name='deal-of-the-day'),
    path('contact-us/', contact_us, name='contact-us'),
    path('videogallery/', videogallery, name='video-gallery'),
    path('imagegallery/', imagegallery, name='image-gallery'),
    path('ProductSearch/',ProductSearchView.as_view(), name = 'search'),
    path('products/price-range-filtering/<pk>/', pricerangefiltering, name='pricerange-filtering'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('buy-now/<slug>/', buy_now, name='buy-now'),
    path('remove-form-cart/<slug>/', remove_form_cart, name='remove-form-cart'),
    path("wish_list/", wish_list, name="wish-list"),
    path('add_to_wishlist/<slug>', add_to_wishlist, name='add-to-wishlist'),
    path('delete_wish_list/<slug>', delete_wish_list, name='delete-wish-list'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path("cart_summary", CartSummary, name="cart-summary"),
    path("my-review", myreview, name="my-review"),
    path('ordered/product/review/<int:pk>/', review, name='order-item-review'),
    path("order_summary", OrderSummary, name="order-summary"),
    path("order_details/<int:pk>", OrderDetails, name="order-detail"),
    path('ordered/product/detail/<int:pk>/', Order_Item_Details, name='order-item-detail'),
    path("PrductQuantityIncrement/<slug>", PrductQuantityIncrement.as_view(), name="Prduct-Quantity-Increment"),
    path("PrductQuantityDecrementr/<slug>", PrductQuantityDecrementr.as_view(), name="Prduct-Quantity-Decrementr"),


    path('profile-dashboard', profile_dashboard, name='profile-dashboard'),
    path('campaign/products/<pk>/', campaign_product_filtering, name='campaign-product'),
    path('order_pdf_view/<pk>',render_order_pdf_view, name='render-order-pdf-view'),

    path('privacy-policy', privacy_policy,name='privacy-policy'),
    path('terms_conditions', terms_conditions,name='terms_conditions'),
    path('shipping_delivery', shipping_delivery,name='shipping_delivery'),
    path('returns_policy', returns_policy,name='returns_policy'),
    path('mission', mission,name='mission'),
    path('vision', vision,name='vision'),
    path('about_us', about_us,name='about_us'),
]
