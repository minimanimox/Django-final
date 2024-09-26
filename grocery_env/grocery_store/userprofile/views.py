from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from .models import Userprofile
from store.forms import ProductForm
from store.models import Product, OrderItem, Order
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
    products = request.user.products.exclude(status=Product.DELETED)
    order_items = OrderItem.objects.filter(product__user=request.user)
    
    return render(request, 'userprofile/staff_page.html', {
        'products': products,
        'order_items': order_items
    })

@login_required
def staff_page_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    return render(request, 'userprofile/staff_page_order_detail.html', {
        'order': order
    })
    
@login_required
def myaccount(request):
    # 현재 로그인한 사용자가 생성한 주문들 가져오기
    orders = Order.objects.filter(created_by=request.user)
    print(f"request user: {request.user}")
    print(f"created_by: {Order.created_by}")

    # 주문 항목 가져오기: 로그인한 사용자가 만든 주문들에 대한 OrderItem
    order_items = OrderItem.objects.filter(order__in=orders)

    # 디버깅: 데이터가 제대로 가져오는지 출력해보기
    print(f"Orders: {orders}")
    print(f"Order Items: {order_items}")

    for order_item in order_items:
        order_item.total_price = order_item.quantity * order_item.product.price
        
    return render(request, 'userprofile/myaccount.html', {
        'orders': orders,
        'order_items': order_items,
    })

def staff_detail(request, pk):
    user = User.objects.get(pk=pk)
    products = user.products.filter(status=Product.ACTIVE)
    
    return render(request, 'userprofile/staff_detail.html', {
        'user': user,
        'products': products,
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
        
            messages.success(request, 'The product was added.')
            
            return redirect('staff_page')
        else:
            print("Form is not valid")
            print(form.errors)  # 폼 에러 출력
    else:
        form = ProductForm()
        
    return render(request, 'userprofile/update_product.html', {
        'title': 'Add product',
        'form': form
    })

@login_required
def edit_product(request, pk):
    product = Product.objects.filter(user=request.user).get(pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'The product was updated.')
            
            return redirect('staff_page')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'userprofile/update_product.html', {
        'title': 'Edit product',
        'product': product,
        'form': form
    })
    
@login_required
def delete_product(request, pk):
    product = Product.objects.filter(user=request.user).get(pk=pk)
    product.status = Product.DELETED
    product.save()
    
    messages.success(request, 'The product was deleted.')
    
    return redirect('staff_page')
    