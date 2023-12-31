from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', views.CustomUserViewSet, basename="user")


# def is_route_selected(url_pattern):
#     urls = [
#         "users/activation/",
#     ]

#     for u in urls:
#         match = url_pattern.resolve(u)
#         print(match)
#         if match:
#             return False
#     return True

# # Filter router URLs removing unwanted ones
# selected_user_routes = list(filter(is_route_selected, router.urls))
# Of course, instead of [] you'd have other URLs from your app here:

# print(router.urls)

urlpatterns = [
    path('auth/', include(router.urls)),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('social_auth.urls')),
    path('auth/admin/', views.AdminListCreateView().as_view()),
    path('auth/admin/<uuid:user_id>/assign-roles/', views.assign_role),
    path('auth/login/', views.user_login, name="login_view"),
    path("auth/logout/", views.logout_view, name="logout_view"),
    path('auth/otp/verify/', views.otp_verification),
    path('auth/otp/new/', views.reset_otp),
    path('auth/fcm-token/', views.update_firebase_token),
    path("auth/users/vendor", views.AddVendorView.as_view(), name="vendor-signup"),
    path("vendors/", views.VendorListView.as_view(), name="vendors-list"),
    path("vendors/<uuid:vendor_id>/update_status/", views.update_vendor_status, name="vendors-status"),
    path("stores/", views.StoreListView.as_view(), name="stores"),
    path("stores/<uuid:id>/", views.StoreDetailView.as_view(), name="store_detail"),
    path("bank-detail/<uuid:id>/", views.BankDetailView.as_view(), name="bank_detail"),
    path("users/my-favourites", views.user_favourites),
    path("users/favourites/<uuid:product_id>", views.update_favorite),
    path("permissions/", views.PermissionList.as_view(), name="permissions"),
    path("modules/", views.ModuleAccessList.as_view(), name="modules"),
    path("roles/", views.GroupListCreate.as_view(), name="roles"),
    path("roles/<int:id>", views.GroupDetail.as_view(), ),
    path("admin/vendors-stat", views.dashboard_vendor_stat,),
    path("activity-logs/", views.activity_logs),
    path("auth/image-upload", views.image_upload, name="image-upload"),
    path("auth/mono-token/", views.get_mono_token, name="get_mono_token"),
    path("referrals/check-code/", views.check_ref_code, name="check-code"),
    
]
