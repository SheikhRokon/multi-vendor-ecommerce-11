from django.urls import path
from .views import *



urlpatterns = [
    path('dashboard/home',dashboard_home, name='dashboard-home'),

    #product
    path('dashboard/product-list', product_list, name='dashboard-product-list'),
    path('dashboard/product/add/', ProductCreate.as_view(), name='create_product'),
    path('dashboard/product-delete/<int:pk>', product_delete, name='dashboard-product-delete'),
    path('dashboard/update/<int:pk>/', ProductUpdate.as_view(), name='product-update'),


    path('dashboard/delete-image/<int:pk>/', delete_image, name='delete_image'),
    path('dashboard/delete-variant/<int:pk>/', delete_variant, name='delete_variant'),

    
    #order
    path('dashboard/all-order',all_order , name='all-order'),
    path('dashboard/order-details/<int:pk>',OrderDetails , name='order-details'),
    path('dashboard/order-update/<int:pk>',order_update , name='order-update'),
    path('dashboard/order-shipping-address-update/<int:pk>',shipping_address_update , name='shippingaddress-update'),
    

    #category
    path('dashboard/category-list',category_list , name='category-list'),
    path('dashboard/inactive-category-list',inactive_category_list , name='inactive-category-list'),
    path('dashboard/category-add',category_add , name='category-add'),
    path('dashboard/category_update/<slug>',category_update , name='category-update'),
    path('dashboard/category-delete/<str:slug>', category_delete, name='category-delete'),


    #brand
    path('dashboard/brand-list',brand_list , name='brand-list'),
    path('dashboard/inactive-brand-list',inactive_brand_list , name='inactive-brand-list'),
    path('dashboard/brand-add',brand_add , name='brand-add'),
    path('dashboard/brand-update/<slug>',brand_update , name='brand-update'),
    path('dashboard/brand-delete/<str:slug>', brand_delete, name='brand-delete'),

    
    #bannerd
    path('dashboard/banner-list',banner_list , name='banner-list'),
    path('dashboard/banner-add',banner_add , name='banner-add'),
    path('dashboard/banner-update/<int:pk>',banner_update , name='banner-update'),
    path('dashboard/banner-delete/<int:pk>', banner_delete, name='banner-delete'),

    #logo
    path('dashboard/logo-list',logo_list , name='logo-list'),
    path('dashboard/logo-add',logo_add , name='logo-add'),
    path('dashboard/logo-update/<int:pk>',logo_update , name='logo-update'),
    path('dashboard/logo-delete/<int:pk>', logo_delete, name='logo-delete'),

    #user
    path('dashboard/user-list',user_list , name='user-list'),
    path('dashboard/user-add',user_add , name='user-add'),
    path('dashboard/user-update/<int:pk>',user_update , name='user-update'),
    path('dashboard/user-delete/<int:pk>', user_delete, name='user-delete'),

    #profile
    path('dashboard/profile-list',profile_list , name='profile-list'),
    path('dashboard/profile-add',profile_add , name='profile-add'),
    path('dashboard/profile-update/<int:pk>',profile_update , name='profile-update'),
    path('dashboard/profile-delete/<int:pk>', profile_delete, name='profile-delete'),


    #coupon
    path('dashboard/coupon-list',coupon_list , name='coupon-list'),
    path('dashboard/coupon-add',coupon_add , name='coupon-add'),
    path('dashboard/coupon-update/<int:pk>',coupon_update , name='coupon-update'),
    path('dashboard/coupon-delete/<int:pk>',coupon_delete , name='coupon-delete'),

    #flashsale
    path('dashboard/flashsale-list',flashsale_list , name='flashsale-list'),
    path('dashboard/flashsale-add',flashsale_add , name='flashsale-add'),
    path('dashboard/flashsale-update/<int:pk>',flashsale_update , name='flashsale-update'),
    path('dashboard/flashsale-delete/<int:pk>',flashsale_delete , name='flashsale-delete'),

    #campaign_category
    path('dashboard/campaign_category-list',campaign_category_list , name='campaign-category-list'),
    path('dashboard/campaign_category-add',campaign_category_add , name='campaign-category-add'),
    path('dashboard/campaign_category-update/<int:pk>',campaign_category_update , name='campaign-category-update'),
    path('dashboard/campaign_category-delete/<int:pk>',campaign_category_delete , name='campaign-category-delete'),


    #campaign_product
    path('dashboard/campaign-product-list',campaign_product_list , name='campaign-product-list'),
    path('dashboard/campaign-product-add',campaign_product_add , name='campaign-product-add'),
    path('dashboard/campaign-product-update/<int:pk>',campaign_product_update , name='campaign-product-update'),
    path('dashboard/campaign-product-delete/<int:pk>',campaign_product_delete , name='campaign-product-delete'),

    #deal_of_the_day
    path('dashboard/deal-of-the-day-product-list',deal_of_the_day_product_list , name='deal_of_the_day_product-list'),
    path('dashboard/deal-of-the-day-product-add',deal_of_the_day_product_add , name='deal_of_the_day_product-add'),
    path('dashboard/deal-of-the-day-product-update/<int:pk>',deal_of_the_day_product_update , name='deal_of_the_day_product-update'),
    path('dashboard/deal-of-the-day-product-delete/<int:pk>',deal_of_the_day_product_delete , name='deal_of_the_day_product-delete'),

    #Rating
    path('dashboard/rating-list',rating_list , name='rating-list'),
    path('dashboard/rating-add',rating_add , name='rating-add'),
    path('dashboard/rating-update/<int:pk>',rating_update , name='rating-update'),
    path('dashboard/rating-delete/<int:pk>',rating_delete , name='rating-delete'),

    #Contact
    path('dashboard/contact-data-list',contact_data_list, name='contact-list'),
    path('dashboard/contact-data-detail/<pk>',contact_data_detail, name='contact-detail'),
    path('dashboard/contact-add',contact_add , name='contact-add'),
    path('dashboard/contact-update/<int:pk>',contact_update , name='contact-update'),
    path('dashboard/contact-delete/<int:pk>',contact_delete , name='contact-delete'),


    #privacy_policy
    path('dashboard/privacy_policy-list',privacy_policy_list, name='privacy_policy-list'),
    path('dashboard/privacy_policy-add',privacy_policy_add , name='privacy_policy-add'),
    path('dashboard/privacy_policy-update/<int:pk>',privacy_policy_update , name='privacy_policy-update'),
    path('dashboard/privacy_policy-delete/<int:pk>',privacy_policy_delete , name='privacy_policy-delete'),


    #terms_condition
    path('dashboard/terms_condition-list',terms_condition_list, name='terms_condition-list'),
    path('dashboard/terms_condition-add',terms_condition_add , name='terms_condition-add'),
    path('dashboard/privacy_policy-update/<int:pk>',terms_condition_update , name='terms_condition-update'),
    path('dashboard/terms_condition-delete/<int:pk>',terms_condition_delete , name='terms_condition-delete'),

    #mission
    path('dashboard/mission-list',mission_list, name='mission-list'),
    path('dashboard/mission-add',mission_add , name='mission-add'),
    path('dashboard/mission-update/<int:pk>',mission_update , name='mission-update'),
    path('dashboard/mission-delete/<int:pk>',mission_delete , name='mission-delete'),


    #vision
    path('dashboard/vision-list',vision_list, name='vision-list'),
    path('dashboard/vision-add',vision_add , name='vision-add'),
    path('dashboard/vision-update/<int:pk>',vision_update , name='vision-update'),
    path('dashboard/vision-delete/<int:pk>',vision_delete , name='vision-delete'),

    #returns_policy
    path('dashboard/returns_policy-list',returns_policy_list, name='returns_policy-list'),
    path('dashboard/returns_policy-add',returns_policy_add , name='returns_policy-add'),
    path('dashboard/returns_policy-update/<int:pk>',returns_policy_update , name='returns_policy-update'),
    path('dashboard/returns_policy-delete/<int:pk>',returns_policy_delete , name='returns_policy-delete'),


    #returns_policy
    path('dashboard/shipping_delivery-list',shipping_delivery_list, name='shipping_delivery-list'),
    path('dashboard/shipping_delivery-add',shipping_delivery_add , name='shipping_delivery-add'),
    path('dashboard/shipping_delivery-update/<int:pk>',shipping_delivery_update , name='shipping_delivery-update'),
    path('dashboard/shipping_delivery-delete/<int:pk>',shipping_delivery_delete , name='shipping_delivery-delete'),

    #aboutus
    path('dashboard/aboutus-list',aboutus_list, name='aboutus-list'),
    path('dashboard/aboutus-add',aboutus_add , name='aboutus-add'),
    path('dashboard/aboutus-update/<int:pk>',aboutus_update , name='aboutus-update'),
    path('dashboard/aboutus-delete/<int:pk>',aboutus_delete , name='aboutus-delete'),






    #image
    path('dashboard/image-list',image_list , name='image-list'),
    path('dashboard/image-add',image_add , name='image-add'),
    path('dashboard/image-update/<int:pk>',image_update , name='image-update'),
    path('dashboard/image-delete/<int:pk>',image_delete , name='image-delete'),

    #video
    path('dashboard/video-list',video_list , name='video-list'),
    path('dashboard/video-add',video_add , name='video-add'),
    path('dashboard/video-update/<int:pk>',video_update , name='video-update'),
    path('dashboard/video-delete/<int:pk>',video_delete , name='video-delete'),
    

    #parcel
    path('create_redx_parcel/<pk>', create_redx_parcel,name='create-redx-parcel'),

]