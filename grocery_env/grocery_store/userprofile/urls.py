from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'), 
    path('login/', auth_views.LoginView.as_view(template_name='userprofile/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('myaccount/', views.myaccount, name='myaccount'),
    path('staff-page/', views.staff_page, name='staff_page'),
    path('staff-page/add-product/', views.add_product, name='add_product'),
    path('staff-page/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('staff-page/delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('staff/<int:pk>/', views.staff_detail, name='staff_detail'),
]
