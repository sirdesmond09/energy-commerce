from django.urls import path
from . import views


urlpatterns = [
    path("categories/", views.CategoryView.as_view(), name="categories"),
    path("categories/<uuid:id>/", views.CategoryDetailView.as_view(), name="category-detail"),
    path("products/new/", views.add_product, name="new-product"),
    path("products/", views.ProductList.as_view(), name="product-list"),
    path("products/<uuid:id>/", views.ProductDetail.as_view(), name="product-detail"),
    path("products/<uuid:product_id>/validate/", views.update_product_status, name="product-detail"),
    path("products/<uuid:product_id>/update-gallery/", views.update_galley, name="gallery-update-delete"),
    path("products/<uuid:product_id>/update-gallery/<uuid:img_id>", views.update_galley, name="gallery-update-delete"),
    path("locations/", views.LocationView.as_view(), name="location"),
    path("locations/<uuid:id>/", views.LocationDetailView.as_view(), name="location-detail"),
    path("product-components/<int:id>/", views.ComponentsDetailView.as_view(), name="product-component-detail"),
    path("addresses/", views.AddressListCreateView.as_view(), name="user-addresses"),
    path("addresses/<uuid:id>/", views.AddressesDetailView.as_view(), name="user-address-detail"),
    path("addresses/<uuid:id>/set-default", views.set_default_address, name="user-address-default"),
    path("orders/new/", views.new_order, name="new-orders"),
    path("orders/", views.OrderList.as_view(), name="all-orders"),
    path("orders/<int:id>", views.OrderDetail.as_view(), name="order-detail"),
    path("orders/<str:booking_id>/accept/<int:item_id>/", views.accept_order, name="order_accept"),
    
    
    # path("orders/<str:booking_id>/cancel/", views.request_order_cancel, name="request_order_cancel"),
    
    path("orders/<str:booking_id>/items/<int:item_id>/cancel/", views.request_order_item_cancel, name="request_orderitem_cancel"),
    
    # path("orders/<str:booking_id>/cancel/respond", views.respond_to_cancel_request, name="respond_order_cancel"),
    path("orders/<str:booking_id>/items/<int:item_id>/cancel/respond", views.respond_to_cancel_request, name="respond_orderitem_cancel"),
    
    
    
    path("orders/<str:booking_id>/clear/", views.permanently_delete_order, name="order_clear"),
    path("orders/<str:booking_id>/outright_payment/", views.outright_payment),
    path("orders/<str:booking_id>/lease_to_own_payment/", views.lease_to_own_payment),
    path("orders/<str:booking_id>/power_as_a_service_payment/", views.power_as_a_service_payment),
    path("orders/<str:booking_id>/item/<int:item_id>", views.order_item_detail),
    path("energy-calculator/", views.energy_calculator),
    path("products/multiple_products_by_id/", views.multiple_products_by_id),
    path("cart/", views.CartListCreateView.as_view(), name="user-cart"),
    path("cart/<int:id>/", views.CartDetailView.as_view(), name="user-cart-detail"),
    # path("delivery-location/", views.DeliveryDetailListCreateView.as_view(),),
    # path("delivery-location/<int:id>", views.DeliveryDetailView.as_view(),),
    path("vendors/products/", views.VendorProductList.as_view()),
    path("vendors/order-items/", views.VendorItemListView.as_view()),
    path("vendors/order-items/<int:id>/update-status", views.vendor_update_item_status),
    path("admin/dashboard/", views.dashboard_stat),
    path("admin/dashboard/analytics", views.admin_dashboard_graph),
    
    path("payouts/", views.PayOutList.as_view(),),
    path("payouts/<int:id>", views.PayOutDetail.as_view(),),
    path("payments/<int:payment_id>/validate", views.validate_payment,),
    path("payments/", views.PaymentListView.as_view()),
    path("payments/<int:id>/", views.PaymentDetailView.as_view()),
    path("ratings/", views.RatingListCreate.as_view()),
    path("ratings/<int:id>/", views.RatingDetailView.as_view()),
    path("orders/by-batch/paid/", views.PaidOrdersView.as_view()),
    path("calculator-items/", views.CalculatorItemListView.as_view()),
    path("calculator-items/create/", views.CalculatorItemCreateView.as_view()),
    path("calculator-items/<int:id>/", views.CalculatorItemDetailView.as_view()),
    
    
    
    
    
    
]
