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
    path('auth/users/admin/', views.AdminListCreateView().as_view()),
    path('auth/login/', views.user_login, name="login_view"),
    path("auth/logout/", views.logout_view, name="logout_view"),
    path('auth/otp/verify/', views.otp_verification),
    path('auth/otp/new/', views.reset_otp),
    path("auth/users/vendor", views.AddVendorView.as_view(), name="vendor-signup"),
    path("vendors/", views.VendorListView.as_view(), name="vendors-list"),
    path("stores/", views.StoreListView.as_view(), name="stores"),
    path("stores/<uuid:id>/", views.StoreDetailView.as_view(), name="store_detail")
    
]
