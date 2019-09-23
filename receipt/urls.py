from django.urls import path
from rest_framework import routers

from receipt import views

from receipt.rest.viewsets import ReceiptViewSet


router = routers.SimpleRouter()
router.register(r'new_api', ReceiptViewSet)


urlpatterns = [
    path('', views.receipts, name='receipts'),
    path('save_data/', views.save_receipt_data, name='save_raw_data'),
    path('api/scan_qr/', views.scan_qr, name='scan_qr_code'),
    path('api/delete/<int:pk>/', views.delete_receipt, name='delete_receipt')
]
urlpatterns += router.urls