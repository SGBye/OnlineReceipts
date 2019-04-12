from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login

from accounts.forms import SignUpForm
from accounts.models import Profile


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            user.profile.register_in_api()
            request.user.profile.is_registered = True
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def get_new_code(request):
    print("IM HERE")
    user = request.user
    print(user.profile.get_new_code())
    if user.profile.get_new_code() == 'ok':
        print('good')
        return HttpResponse("Check your phone and enter the code to your profile", status=200)
    else:
        return HttpResponse('Such user is not found', status=404)


def save_sms_code(request):
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            print("atuh")
            Profile.objects.filter(pk=user.profile.pk).update(sms_code=str(request.POST.get('sms')))
            return redirect('/')