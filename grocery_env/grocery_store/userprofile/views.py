from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils.text import slugify
from store.models import Product, Category
from .models import Userprofile
from store.forms import ProductForm

import uuid

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            
            login(request, user)
            
            userprofile = Userprofile.objects.create(user=user)
            
            return redirect('frontpage')
    else:
        form = UserCreationForm()
        
    return render(request, 'userprofile/signup.html', {
        'form': form
    })

@login_required    
def staff_page(request):
    return render(request, 'userprofile/staff_page.html')

@login_required
def myaccount(request):
    return render(request, 'userprofile/myaccount.html')


def staff_detail(request, pk):
    user = User.objects.get(pk=pk)
    
    return render(request, 'userprofile/staff_detail.html', {
        'user': user
    })

@login_required
def add_product(request):
    print(request.method)

    if request.method == 'POST':
        print("in if statement")
        
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            print("valid")
            product_name = request.POST.get('product_name')
            product = form.save(commit=False)
            print(f"Product form saved with commit=False: {product}")  # 디버깅용 로그 추가
            product.user = request.user
            product.slug = slugify(f"{product_name}-{uuid.uuid4().hex[:6]}")  # 고유한 slug 생성
            print(f"Product slug generated: {product.slug}")  # 디버깅용 로그 추가
            product.save()
            print(f"Product saved: {product}")  # 디버깅용 로그 추가
            
            return redirect('staff_page')
        else:
            print("Form is not valid")
            print(form.errors)  # 폼 에러 출력
    else:
        form = ProductForm()
        
    return render(request, 'userprofile/add_product.html', {'form': form})