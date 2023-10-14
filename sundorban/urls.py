
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/', include('allauth.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('store.urls')),
    path('', include('paymentApp.urls')),
    path('', include('userapp.urls')),
    path('', include('daseboard.urls')),
    path('', include('other_vendors.urls')),
    # path('oauth/', include('social_django.urls', namespace='social')), 

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)