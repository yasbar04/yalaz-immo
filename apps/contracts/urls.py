from django.urls import path
from . import views

urlpatterns = [
    path('', views.contracts_list, name='contracts_list'),
    path('new/', views.contract_type_selector, name='contract_type_selector'),
    path('new/<str:contract_type>/', views.contract_create, name='contract_create'),
    path('<int:pk>/', views.contract_detail, name='contract_detail'),
    path('<int:pk>/signer/', views.contract_sign, name='contract_sign'),
    path('<int:pk>/pdf/', views.contract_pdf, name='contract_pdf'),
    path('<int:pk>/delete/', views.contract_delete, name='contract_delete'),
]
