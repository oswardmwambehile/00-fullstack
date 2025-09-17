from django.urls import path
from . import views

urlpatterns = [

    path('', views.login_user, name='login'),
    path('add-visit/', views.add_visit, name='add_visit'),
    path('logout/', views.logout_user, name='logout'),
     path('visit/<int:visit_id>/', views.visit_detail, name='visit_detail'),
     path('adminvisit/<int:visit_id>/', views.visit_details, name='visit_details'),
    path('new_visit/', views.new_visit, name='new_visit'),
     path('profile/', views.profile_view, name='profile'),
      path('admin-profile/', views.adminprofile_view, name='profiles'),
     path('add_user/', views.register, name='register'),
     path('change-password/', views.change_password, name='change_password'),
     path('adminchange-password/', views.adminchange_password, name='changes_password'),
      path('adminall_visits/', views.adminall_visit_list, name='all_visit_lists'),
    path('visit/<int:visit_id>/update/', views.update_visit, name='update_visit'),
    path('all_visits/', views.all_visit_list, name='all_visit_list'),# You can replace 'index' with a home view too
    path("get-contacts/<int:company_id>/", views.get_contacts, name="get_contacts"),
    path("get-contact-details/<int:contact_id>/", views.get_contact_details, name="get_contact_details"),
   # urls.py
path(
    "get-contact-details-update/<int:contact_id>/",
    views.get_contact_details_update,
    name="get_contact_details_update"
),
 path('visit-history/<int:visit_id>/history/', views.visit_history, name='visit_history'),

]