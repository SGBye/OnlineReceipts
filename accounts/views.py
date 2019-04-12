from django.shortcuts import render, redirect
from django.contrib.auth import login

from accounts.forms import SignUpForm
from receipt.models import Receipt


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Receipt.register_in_api(user.email, user.username, user.profile.phone)
            request.user.profile.is_registered = True
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
