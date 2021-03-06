import ast
import json

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, HttpResponse, redirect
from urllib.parse import parse_qs

from receipt.forms import ReceiptDataForm
from .models import Receipt


def parse_string(string):
    parsed_string = parse_qs(string)
    result = {'time': parsed_string['t'][0], 'summ': float(parsed_string['s'][0]) * 100, 'fn': parsed_string['fn'][0],
              'fd': parsed_string['i'][0], 'fp': parsed_string['fp'][0], 'n': parsed_string['fp'][0]}
    return result


def home(request):
    form = ReceiptDataForm()
    if request.user.is_authenticated:
        return render(request, 'base.html',
                      {'form': form, 'sms_code': request.user.profile.sms_code})
    return render(request, 'base.html')


@login_required
def receipts(request):
    if request.user.is_authenticated:
        items = list(request.user.receipts.all())
        for i in items:
            i.items = ast.literal_eval(i.items)
            for j in i.items:
                j['price'] /= 100
                j['sum'] /= 100
        if request.user.receipts.all().count() > 0:
            total_summ = round(request.user.receipts.aggregate(Sum('summ'))['summ__sum'], 2)
        else:
            total_summ = 0
        context = {'pre_receipts': items, "total_summ": total_summ}
        return render(request, 'receipts.html', context=context)
    else:
        return render(request, 'receipts.html')


@login_required
def save_receipt_data(request):
    if request.method == "POST":
        form = ReceiptDataForm(request.POST)
        user = request.user
        if form.is_valid():
            if user.profile.login_to_api() != 200:
                return HttpResponse(status=404)

            if user.profile.check_existance(parse_string(form.cleaned_data['receipt_string'])) != 204:
                return HttpResponse("make sure you have confirmed the sms-code", status=404)

            user.profile.get_real_receipt(parse_string(form.cleaned_data['receipt_string']))
            return redirect('/receipts')
        else:
            print("invalid")
    else:
        form = ReceiptDataForm()
    return render(request, 'fromString.html', {'form': form})


@login_required
def scan_qr(request):
    if request.method == "POST":
        user = request.user
        r = requests.post(settings.QR_CODE_URL, files=request.FILES)
        response = r.json()
        receipt_data = response[0]['symbol'][0]['data']

        if user.profile.login_to_api() != 200:
            return HttpResponse(status=404)

        if user.profile.check_existance(parse_string(receipt_data)) != 204:
            return HttpResponse(status=404)

        user.profile.get_real_receipt(parse_string(receipt_data))

        return HttpResponse(status=200)

    else:
        return render(request, 'fromQr.html')


@login_required()
def delete_receipt(request):
    print(request.method)
    if request.method == "DELETE":
        receipt_id = json.loads(request.body)['id']
        print(receipt_id)
        try:
            print('all cool')
            Receipt.objects.get(pk=receipt_id).delete()
            return HttpResponse(status=200)
        except Receipt.DoesNotExist:
            return HttpResponse(status=404)
