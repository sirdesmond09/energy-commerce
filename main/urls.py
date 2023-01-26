from django.urls import path
from . import views


urlpatterns = [
    path("categories/", views.CategoryView.as_view(), name="categories"),
    path("categories/<uuid:id>/", views.CategoryDetailView.as_view(), name="category-detail"),
    path("products/new/", views.add_product, name="new-product"),
    path("products/", views.ProductList.as_view(), name="product-list"),
    path("products/<uuid:id>/", views.ProductDetail.as_view(), name="product-detail"),
    path("products/<uuid:product_id>/update-gallery/<uuid:img_id>", views.update_galley, name="gallery-update-delete"),
    path("locations/", views.LocationView.as_view(), name="location"),
    path("locations/<uuid:id>/", views.LocationDetailView.as_view(), name="location-detail"),
    path("product-components/<int:id>/", views.ComponentsDetailView.as_view(), name="product-component-detail"),
    path("addresses/", views.AddressListCreateView.as_view(), name="user-addresses"),
    path("addresses/<uuid:id>/", views.AddressesDetailView.as_view(), name="user-address-detail"),
    path("orders/new/", views.new_order, name="new-orders"),
    path("energy-calculator/", views.energy_calculator)
    
]
