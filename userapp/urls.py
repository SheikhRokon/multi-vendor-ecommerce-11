from django.urls import path
from userapp import views
from django.contrib.auth import views as auth_views
from userapp import views as user_views
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.decorators import login_required


urlpatterns =[
    path("register/", views.register, name="register"),
    path('customer-login/', views.customer_login, name="customer-login"),
    path('logout/', auth_views.LogoutView.as_view(template_name='userapp/logout.html'), name='logout'),
    path('profile/', user_views.profile, name='profile'),
    path('profile/update', login_required(user_views.profileupdate,login_url='/customer-login/'), name='profile-update'),
    path('password_change/',auth_views.PasswordChangeView.as_view(template_name='userapp/password_change.html'),name='password_change'),
    path('password_change/done/',auth_views.PasswordChangeDoneView.as_view(template_name='userapp/password_change_done.html'),name='password_change_done'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='userapp/password_reset.html'),name='password_reset'),
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='userapp/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='userapp/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='userapp/password_reset_complete.html'), name='password_reset_complete'),
]
