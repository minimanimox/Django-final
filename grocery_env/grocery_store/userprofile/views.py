from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from .models import Userprofile
from store.forms import ProductForm
from userprofile.forms import UserProfileForm, CustomPasswordChangeForm
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
def profile_update(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('myaccount')  # 업데이트 후 myaccount로 리다이렉트
    else:
        user_form = UserProfileForm(instance=request.user)

    return render(request, 'userprofile/profile_update.html', {
        'user_form': user_form
    })

@login_required
def password_change(request):
    if request.method == 'POST':
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # 로그아웃 방지
            messages.success(request, 'Your password was successfully updated!')
            return redirect('myaccount')  # 업데이트 후 myaccount로 리다이렉트
    else:
        password_form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'userprofile/password_change.html', {
        'password_form': password_form
    })
    
@login_required    
def staff_page(request):
    products = Product.objects.exclude(status=Product.DELETED)
    
    # 모든 주문 항목을 가져오기
    order_items = OrderItem.objects.all()

    # 주문 정보 가져오기 (OrderItem을 통해 가져온 주문, 최신 순으로 정렬)
    orders = Order.objects.filter(id__in=order_items.values_list('order_id', flat=True)).distinct().order_by('-id')

    # 각 주문별로 총 금액 계산
    order_totals = {}
    for order in orders:
        # 해당 주문의 OrderItem을 필터링하여 Product.price와 quantity로 총 금액 계산
        total = sum(item.product.price * item.quantity for item in order.items.all())  # Product.price로 계산
        order_totals[order.id] = total
        
        # 디버깅 출력: 각 주문의 총 금액이 제대로 계산되는지 확인
        print(f"Order ID: {order.id}, Total: {total}")
    
    # 디버깅 출력: 최종 order_totals 딕셔너리 확인
    print(f"Order Totals: {order_totals}")
    
    return render(request, 'userprofile/staff_page.html', {
        'orders': orders,
        'products': products,
        'order_items': order_items,
        'order_totals': order_totals,  # 총 금액을 템플릿에 전달
    })
    
@login_required
def staff_page_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    return render(request, 'userprofile/staff_page_order_detail.html', {
        'order': order
    })
 
@login_required
def change_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # 상태 변경 로직 (여기서는 순환 방식으로 처리)
    if order.status == Order.PENDING:
        order.status = Order.APPROVED
    elif order.status == Order.APPROVED:
        order.status = Order.DENIED
    else:
        order.status = Order.PENDING
    
    order.save()

    messages.success(request, f'Order number: {order.id} Status was successfully updated to {order.status}.')
    
    return redirect('staff_page')

@login_required
def customer_list(request):
    # 모든 고객 목록을 가져옵니다.
    customers = User.objects.all()

    return render(request, 'userprofile/customer_list.html', {
        'customers': customers
    })

@login_required
def customer_orders(request, user_id):
    # 해당 고객의 주문 목록을 가져옵니다.
    customer = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(created_by=customer)

    return render(request, 'userprofile/customer_orders.html', {
        'customer': customer,
        'orders': orders
    })
    
@login_required
def customer_detail(request, user_id):
    # user_id를 기준으로 고객 정보 가져오기
    customer = get_object_or_404(User, id=user_id)

    return render(request, 'userprofile/customer_detail.html', {
        'customer': customer,
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
        order_totals[item.order.id] += item.quantity * item.product.price
        # 주문 상태 저장
        order_statuses[item.order.id] = item.order.status

        # 각 주문 항목이 그룹화되는 과정 디버깅
        # print(f"Order ID: {item.order.id}, Product: {item.product.product_name}, Quantity: {item.quantity}, Price: {item.price}")
        # print(f"Grouped Order Items: {grouped_order_items}")
        # print(f"Order Totals: {order_totals}")

    grouped_items = sorted(grouped_order_items.items(), key=lambda x: x[0], reverse=True)
    
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
    # 일반 사용자는 수정 권한이 없으므로 staff만 수정 가능
    if request.user.is_staff:
        
        product = get_object_or_404(Product, pk=pk)

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
    # 일반 사용자는 삭제 권한이 없으므로 staff만 삭제 가능
    if request.user.is_staff:
        
        product = get_object_or_404(Product, pk=pk)
        product.status = Product.DELETED
        product.save()

        messages.success(request, 'The product was deleted.')
        return redirect('staff_page')
        