from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    # Редирект с главной страницы на список товаров
    path('', RedirectView.as_view(url='/products/', permanent=False)),
]