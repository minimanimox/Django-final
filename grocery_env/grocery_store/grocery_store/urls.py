from django.contrib import admin
from django.urls import path, include
from core.views import frontpage, about

urlpatterns = [
    path('', include('store.urls')),  #가장 상단에 둘것
    path('', frontpage, name='frontpage'),
    path('admin/', admin.site.urls),
    path('about/', about, name='about'),
]
