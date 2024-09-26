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
from collections import defaultdict
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
    # 현재 로그인한 사용자의 주문들 가져오기
    orders = Order.objects.filter(created_by=request.user)
    
    # 주문 항목 가져오기
    order_items = OrderItem.objects.filter(order__in=orders)
    
    # 주문 별로 그룹화 및 총 금액 계산
    grouped_order_items = defaultdict(list)
    order_totals = {}
    order_statuses = {}  # 주문 상태 저장
    
    # 디버깅을 위한 print 문
    print(f"Orders: {orders}")  # 사용자의 주문 목록
    print(f"Order Items: {order_items}")  # 주문 항목 목록
    
    for item in order_items:
        grouped_order_items[item.order.id].append(item)
        if item.order.id not in order_totals:
            order_totals[item.order.id] = 0
        order_totals[item.order.id] += item.quantity * item.price
        # 주문 상태 저장
        order_statuses[item.order.id] = item.order.status

        # 각 주문 항목이 그룹화되는 과정 디버깅
        # print(f"Order ID: {item.order.id}, Product: {item.product.product_name}, Quantity: {item.quantity}, Price: {item.price}")
        # print(f"Grouped Order Items: {grouped_order_items}")
        # print(f"Order Totals: {order_totals}")

    print("test")        
    print(grouped_order_items.items())
    grouped_items = grouped_order_items.items()
    
    return render(request, 'userprofile/myaccount.html', {
        'grouped_items': grouped_items,
        'grouped_order_items': grouped_order_items,  # 그룹화된 주문 항목
        'order_totals': order_totals,  # 주문별 총합 계산
        'order_statuses': order_statuses,  # 주문 상태 전달
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
    