from rest_framework import viewsets

from receipt.models import Receipt
from rest.serializers import ReceiptSerializer


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        super().create(request, *args, **kwargs)