from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth, messages
from django.db.models import Q
from .models import Category, News, Banner
from .forms import CategoryForm, NewsForm, BannerForm
from django.apps import apps
from users.models import *
from django.db.models import Count

Account = apps.get_model('accounts', 'Account')

# Create your views here.

#Admin Home
def admin_home(request):
    if 'super_email' in request.session:
        tokens = Token.objects.all()
        total_tokens = tokens.count()
        categories = Category.objects.annotate(token_count=Count('token'))
        total_users = Account.objects.count()
        wallet = request.user.wallet_obj
        transaction_history = wallet.transaction_history
        sales_profit = commission_profit = commission_and_sales_profit = balance = purchase_amount = 0
        rows = []

        for transaction in transaction_history:
            try:
                if 'Received' in transaction:
                    if 'for token' in transaction:
                        # Received profit from token sale
                        amount = float(transaction.split('Received ')[1].split(' for token')[0])
                        sales_profit += amount
                        rows.append({'type': 'Sale', 'description': f'Token Sale ({transaction})', 'amount': amount})
                    else:
                        # Received commission
                        amount = float(transaction.split('Received ')[1].split(' commission')[0])
                        commission_profit += amount
                        commission_and_sales_profit += amount
                        rows.append({'type': 'Commission', 'description': f'Commission ({transaction})', 'amount': amount})
                else:
                    # Paid for token purchase
                    amount = float(transaction.split('Paid ')[1].split(' for token')[0])
                    purchase_amount += amount
                    commission_and_sales_profit -= amount
                    rows.append({'type': 'Purchase', 'description': f'Token Purchase ({transaction})', 'amount': amount})
            except ValueError:
                pass

        commission_and_sales_profit = sales_profit + commission_profit
        balance = wallet.balance
        context = {
            'sales_profit': sales_profit,
            'commission_profit': commission_profit,
            'commission_and_sales_profit': commission_and_sales_profit,
            'balance': balance,
            'purchase_amount': purchase_amount,
            'wallet': wallet,
            'total_tokens': total_tokens,
            'total_users': total_users,
            'categories': categories,
            'rows': rows
        }
        return render(request, 'admins_temp/admin-home.html', context)
    else:
        return redirect('admin_login')



#Admin items
def admin_items(request):
    user = request.user
    if 'q' in request.GET:
        q = request.GET['q']
        tokens = Token.objects.filter(Q(brand__icontains=q) | Q(name__icontains=q))
        liked_products = Like.objects.filter(owner=user, likes=True)
        liked_tokens = {liked_product.token.id for liked_product in liked_products}
    else:
        tokens = Token.objects.filter(is_active=True).order_by('id')
        liked_products = Like.objects.filter(owner=user, likes=True)
        liked_tokens = {liked_product.token.id for liked_product in liked_products}
    context = {'tokens': tokens, 'liked_tokens': liked_tokens}
    return render(request, 'admins_temp/admin-items.html', context)



#User Controls
def admin_user_control(request):
    if 'q' in request.GET:
        q = request.GET['q']
        data = Account.objects.filter(Q(username__icontains=q) | Q(email__icontains=q))
    else:
        data = Account.objects.all()

    context = {'data': data,}
    return render(request, 'admins_temp/admin-user.html', context)



#Admin Wallet Page
def admin_wallet(request):
    wallet = request.user.wallet_obj
    transaction_history = wallet.transaction_history
    sales_profit = commission_profit = commission_and_sales_profit = balance = 0
    for transaction in transaction_history:
        try:
            if 'Received' in transaction:
                if 'for token' in transaction:
                    # Received profit from token sale
                    sales_profit += float(transaction.split('Received ')[1].split(' for token')[0])
                else:
                    # Received commission
                    commission_profit += float(transaction.split('Received ')[1].split(' commission')[0])
                    commission_and_sales_profit += float(transaction.split('Received ')[1].split(' commission')[0])
            else:
                commission_and_sales_profit -= float(transaction.split('Paid ')[1].split(' for token')[0])
        except ValueError:
            pass
    commission_and_sales_profit = sales_profit + commission_profit
    balance = wallet.balance
    context = {
        'sales_profit': sales_profit,
        'commission_profit': commission_profit,
        'commission_and_sales_profit': commission_and_sales_profit,
        'balance': balance,
        'wallet': wallet,
    }
    return render(request, 'admins_temp/admin-wallet.html', context)



#Admin base
def admin_base(request):
    return render(request, 'admins_temp/admin-base.html')



#Admin logout
def admin_logout(request):
    auth.logout(request)
    messages.success(request,'you are logged out')
    return redirect('admin_login')



#Admin login
def admin_login(request):
    if request.method == 'POST':
        email       = request.POST['email']
        password    = request.POST['password']

        user = auth.authenticate(email=email,password=password)

        if user is not None and user.is_superadmin:
            request.session['super_email'] = email
            login(request, user)
            return redirect('admin_home')
        else:
            messages.info(request, 'Admin not Exist')
            return redirect('admin_login')
    else:
        return render(request, 'admins_temp/admin-login.html')
    



#Block user
def block_user(request, user_id):
    user = Account.objects.get(id=user_id)
    user.is_active = False
    user.save()
    return redirect('admin_user_control')



#UnBlock user
def unblock_user(request, user_id):
    user = Account.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return redirect('admin_user_control')



#Category
def category(request):
    data = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category')
    else:
        form = CategoryForm()
    context = {'data': data, 'form': form}
    return render(request, 'admins_temp/admin-category.html', context)

    


#Listing Categories
def list(request, cat_id):
    cat = Category.objects.get(id=cat_id)
    cat.is_active = True
    cat.save()
    return redirect('category')



#UnListing Categories
def unlist(request, cat_id):
    cat = Category.objects.get(id=cat_id)
    cat.is_active = False
    cat.save()
    return redirect('category')



#Edit Category
def edit(request, cat_id):
    data = Category.objects.all()
    cat = Category.objects.get(id=cat_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=cat)
        if form.is_valid():
            form.save()
            return redirect('category')
    else:
        form = CategoryForm(instance=cat)
    context = {'form': form, 'data': data}
    return render(request, 'admins_temp/admin-category.html', context)



#News Management
def news(request):
    data = News.objects.all()
    banner_data = Banner.objects.all()
    context = {'data': data, 'banner_data': banner_data}
    return render(request, 'admins_temp/admin-news.html', context)



#Edit News
def edit_news(request, id):
    news_item = News.objects.get(id=id)

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news_item)
        if form.is_valid():
            form.save()
            return redirect('news')
    else:
        form = NewsForm(instance=news_item)

    context = {'form': form, 'news_item': news_item}
    return render(request, 'admins_temp/admin-news-edit.html', context)



#Edit Banner
def edit_banner(request, id):
    banner_items = Banner.objects.get(id=id)

    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner_items)
        if form.is_valid():
            form.save()
            return redirect('news')
    else:
        form = BannerForm(instance=banner_items)

    context = {'form': form, 'banner_items': banner_items}
    return render(request, 'admins_temp/admin-banner-edit.html', context)