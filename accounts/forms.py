from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import TextInput

from .models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput())
    phone = forms.CharField(widget=TextInput(attrs={'type': 'tel'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        phone = '+'+''.join(k for k in phone if k.isdigit())
        if Profile.objects.filter(phone=phone).exists():
            raise ValidationError("Пользователь с таким номером телефона уже существует")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.cleaned_data["phone"]
        if commit:
            user.save()
        return user


class SmsCodeForm(forms.Form):
    sms_code = forms.CharField(label="Please, enter the code from sms. It's needed to access api", max_length=6)
