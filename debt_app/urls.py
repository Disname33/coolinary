from django.urls import path

from .views import debt_info, debt_admin, debt_create

urlpatterns = [
    path('info/', debt_info, name='debt_info'),
    path('admin/', debt_admin, name='debt_admin'),
    path('create/', debt_create, name='debt_create'),
]
