from django.urls import path

from receipt import views

urlpatterns = [
    path('', views.receipts, name='receipts'),
    path('save_data/', views.save_receipt_data, name='save_raw_data'),
    path('api/scan_qr/', views.scan_qr, name='scan_qr_code'),
    path('api/delete/<str:pk>/', views.delete_receipt, name='delete_receipt')
]