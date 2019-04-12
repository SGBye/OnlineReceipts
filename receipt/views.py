import ast

import requests
from django.conf import settings
from django.db.models import Sum
from django.shortcuts import render, HttpResponse, redirect
from urllib.parse import parse_qs

from receipt.forms import ReceiptDataForm
from .models import ReceiptData, Receipt


def parse_string(string):
    parsed_string = parse_qs(string)
    result = {'time': parsed_string['t'][0], 'summ': float(parsed_string['s'][0]) * 100, 'fn': parsed_string['fn'][0],
              'fd': parsed_string['i'][0], 'fp': parsed_string['fp'][0], 'n': parsed_string['fp'][0]}
    return result


def home(request):
    title = "Индексовая страница"
    form = ReceiptDataForm()
    if request.user.is_authenticated:
        return render(request, 'base.html',
                      {'form': form, "pre_receipts": request.user.pre_receipts.all(), 'title': title})
    return render(request, 'base.html', {'form': form, 'title': title})


def receipts(request):
    if request.user.is_authenticated:
        items = list(request.user.receipts.all())
        for i in items:
            i.items = ast.literal_eval(i.items)
            for j in i.items:
                j['price'] /= 100
                j['sum'] /= 100
        total_summ = request.user.receipts.aggregate(Sum('summ'))['summ__sum']
        context = {'pre_receipts': items, "summ": request.user.receipts.last().summ,
                   "total_summ": total_summ}
        return render(request, 'receipts.html', context=context)
    else:
        return render(request, 'receipts.html')


def save_receipt_data(request):
    if request.method == "POST":
        form = ReceiptDataForm(request.POST)
        user = request.user
        if form.is_valid():
            ReceiptData.create_from_dict(parse_string(form.cleaned_data['receipt_string']), user=request.user)
            Receipt.login_to_api(user.profile.phone, user.profile.sms_code)
            request.user.profile.is_logon = True
            Receipt.check_existance(parse_string(form.cleaned_data['receipt_string']), user)
            Receipt.get_real_receipt(parse_string(form.cleaned_data['receipt_string']), user)
            return redirect('/receipts')
        else:
            print("invalid")
    else:
        form = ReceiptDataForm()
    return render(request, 'base.html', {'form': form})


def scan_qr(request):
    if request.method == "POST":
        user = request.user
        print(request.FILES)
        r = requests.post(settings.QR_CODE_URL, files=request.FILES)
        response = r.json()
        receipt_data = response[0]['symbol'][0]['data']

        ReceiptData.create_from_dict(parse_string(receipt_data), user=request.user)

        Receipt.login_to_api(user.profile.phone, user.profile.sms_code)

        Receipt.check_existance(parse_string(receipt_data), user)

        Receipt.get_real_receipt(parse_string(receipt_data), user)

        return HttpResponse(status=200)
