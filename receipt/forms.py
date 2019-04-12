from django import forms
from django.core.exceptions import ValidationError


class ReceiptDataForm(forms.Form):
    receipt_string = forms.CharField(label='Your receipt data  ', max_length=100,
                                     widget=forms.TextInput(
                                         attrs={
                                             'placeholder': 'Enter the data from the scanned QR code',
                                         }
                                     )
                                     )

    def clean_receipt_string(self):
        needed_keys = ['t', 's', 'fn', 'i', 'fp', 'n']
        data = self.cleaned_data['receipt_string']
        if not all(k in data for k in needed_keys):
            raise ValidationError("Invalid format of QR code. Please, try again. ")
        else:
            return data


class ReceiptImageDataForm(forms.Form):
    photo = forms.ImageField()
