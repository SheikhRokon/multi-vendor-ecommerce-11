from django.urls import path
from .views import *


urlpatterns = [
    path("vendor_registaion_step_1/", vendor_registaion_step_1, name="vendor_registaion_step_1"),
    # path("vendor_registaion_step_2/", vendor_registaion_step_2, name="vendor_registaion_step_2"),
    path("vendor_login/", vendor_login, name="vendor_login"),
    path("vendor_full_info/", vendor_profile_update, name="vendor_full_info"),
    path("vendor_pro/", vendor_pro, name="vendor_pro"),
    path("vendor_dashvoard/", vendor_dashvoard, name="vendor_dashvoard"),
    path("vendor_pro_update/", vendor_pro_update, name="vendor_pro_update"),

]
