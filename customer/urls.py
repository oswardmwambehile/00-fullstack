from django.urls import path
from . import views

urlpatterns = [
 path("add/", views.add_customer, name="add_customer"),
    path("list/", views.customer_list, name="customer_list"),
     path('users/', views.user_list, name='user_list'),
     path('index', views.index, name='index'),
     path('users/', views.user_list, name='user_list'),
      path("customer-list/", views.admincustomer_list, name="customers_list"),
       path("customers-update/<int:pk>/update/", views.adminupdate_customer, name="updates_customer"),
     path('users-edit/<int:user_id>/edit/', views.edit_user, name='edit_user'),
      path('users_disable/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
     path("delete/<int:pk>/", views.delete_customer, name="delete_customer"),
     path("customers/<int:pk>/update/", views.update_customer, name="update_customer"),
     path("deletecustomer/<int:pk>/", views.admindelete_customer, name="deletes_customer"),
      path('users/<int:user_id>/', views.user_detail, name='user_detail'),
      path("products/<int:pk>/", views.product_detail, name="product_detail"), 
      path("products-customer/<int:pk>/", views.customerproduct_detail, name="product_details"),
       path("products-admincustomer/<int:pk>/", views.admincustomerproduct_detail, name="adminproduct_details"), # ✅ new
      path('customers/<int:customer_id>/view/', views.view_customer, name='view_customer'),
      path('customers-admin/<int:customer_id>/view/', views.adminview_customer, name='views_customer'),
    
]