

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Wallet

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, password=password)
        Wallet.objects.create(user=user)
        return redirect('login')
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Wallet, Transaction
from django.contrib.auth.models import User

@login_required
def dashboard(request):
    wallet = Wallet.objects.get(user=request.user)
    transactions = Transaction.objects.filter(sender=request.user) | Transaction.objects.filter(recipient=request.user)
    return render(request, 'dashboard.html', {'wallet': wallet, 'transactions': transactions})

@login_required
def add_money(request):
    if request.method == 'POST':
        amount = float(request.POST['amount'])
        wallet = Wallet.objects.get(user=request.user)
        wallet.balance += amount
        wallet.save()
        return JsonResponse({'message': 'Money added successfully', 'balance': wallet.balance})

@login_required
def transfer_money(request):
    if request.method == 'POST':
        recipient_username = request.POST['recipient']
        amount = float(request.POST['amount'])
        sender_wallet = Wallet.objects.get(user=request.user)
        recipient_user = User.objects.get(username=recipient_username)
        recipient_wallet = Wallet.objects.get(user=recipient_user)

        if sender_wallet.balance >= amount:
            sender_wallet.balance -= amount
            recipient_wallet.balance += amount
            sender_wallet.save()
            recipient_wallet.save()
            Transaction.objects.create(sender=request.user, recipient=recipient_user, amount=amount)
            return JsonResponse({'message': 'Transfer successful'})
        else:
            return JsonResponse({'error': 'Insufficient balance'})
