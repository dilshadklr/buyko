from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),

    # Banner
    path('add-banner/', views.add_banner, name='add_banner'),
    path('delete-banner/<int:banner_id>/', views.delete_banner, name='delete_banner'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('adminhome/', views.adminhome, name='adminhome'),

    # Category
    path('category/<str:category_name>/', views.category_page, name='category_page'),

    # CART (SESSION BASED)
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-cart/<int:product_id>/', views.remove_cart, name='remove_cart'),

    # quantity update
    path("cart/increase/<int:item_id>/", views.increase_quantity, name="increase_quantity"),
    path("cart/decrease/<int:item_id>/", views.decrease_quantity, name="decrease_quantity"),

    # Checkout / Orders
    path('cart/checkout/', views.cart_checkout, name='cart_checkout'),
    path('cod-payment/<int:id>/', views.cod_payment, name='cod_payment'),
    path("order-success/", views.order_success, name="order_success"),

    #login
    path("login/", views.login_user, name="login_user"),
    path("register/", views.register_user, name="register_user"),
    path("logout/", views.logout_user, name="logout_user"),

    #PAYMENT
    path('razorpay/create/<int:product_id>/', views.razorpay_create_order, name='razorpay_create_order'),
    path('razorpay/cart/create/', views.razorpay_cart_payment, name='razorpay_cart_payment'),
    path('razorpay/verify/', views.razorpay_verify, name='razorpay_verify'),
    path('razorpay/verify/single/', views.razorpay_verify_single, name='razorpay_verify_single'),

    #ORDERS/DETAILS
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('user-details/', views.user_details, name='user_details'),
    path('user-details/', views.user_details, name='user_details'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    #password
    path("password_reset/", views.password_reset_request, name="password_reset_request"),
    path("password_reset/verify/", views.password_reset_verify, name="password_reset_verify"),
    path("password_reset/confirm/", views.password_reset_confirm, name="password_reset_confirm"),

    #users/stock
     path('admin-users/', views.admin_users, name='admin_users'),
     path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
     path('admin-stock/', views.admin_stock, name='admin_stock'),

    #sales report
    path("sales-report/", views.sales_report, name="sales_report"),
    path('sales-report/pdf/', views.sales_report_pdf, name='sales_report_pdf'),
]



