from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import TokenForm
from django.apps import apps
from .models import *
from accounts.forms import Profileform
from django.contrib import messages
from razorpay import Client
import json
from django.conf import settings
from django.http import JsonResponse
from admins.models import News
import razorpay
import decimal
from django.db.models import Q
from django.urls import reverse
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from admins.models import Banner

Account = apps.get_model('accounts', 'Account')
Category = apps.get_model('admins', 'Category')
# Create your views here.



#Home
def home(request):
    tokens = Token.objects.filter(is_active=True).order_by('-likes_count')[:8]
    liked_tokens = set()
    news = News.objects.all()
    banners = Banner.objects.all()
    if request.user.is_authenticated:
        liked_products = Like.objects.filter(owner=request.user, likes=True)
        liked_tokens = {liked_product.token.id for liked_product in liked_products}
    context = {'tokens': tokens, 'liked_tokens': liked_tokens, 'news': news, 'banners': banners}
    return render(request, 'users_temp/index.html', context)



#Items
@login_required(login_url='/accounts/login_user/')
def items(request):
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
    return render(request, 'users_temp/items.html', context)



#Token Bidding
def token_bidding(request):
    return render(request, 'users_temp/token-bidding.html')


#Catogories
@login_required(login_url='/accounts/login_user/')
def categories(request, category=None):
    if category is None:
        category = 'characters'
    elif category not in ['characters', 'sports', 'music']:
        return redirect('categories', category='characters')

    sort = request.GET.get('sort', 'name')

    # filter tokens by amount
    amount_filter = request.GET.get('amount', None)
    if amount_filter == 'lt5000':
        tokens = Token.objects.filter(category__name=category, price__lt=5000)
    elif amount_filter == '5000_10000':
        tokens = Token.objects.filter(category__name=category, price__gte=5000, price__lt=10000)
    elif amount_filter == '10000_15000':
        tokens = Token.objects.filter(category__name=category, price__gte=10000, price__lt=15000)
    elif amount_filter == '15000_20000':
        tokens = Token.objects.filter(category__name=category, price__gte=15000, price__lt=20000)
    elif amount_filter == 'gte20000':
        tokens = Token.objects.filter(category__name=category, price__gte=20000)
    else:
        tokens = Token.objects.filter(category__name=category)

    # sort tokens
    if sort == 'name':
        tokens = tokens.order_by('name')
    elif sort == 'price_asc':
        tokens = tokens.order_by('price')
    elif sort == 'price_desc':
        tokens = tokens.order_by('-price')
    else:
        return redirect('categories', category=category)

    context = {'tokens': tokens, 'category': category, 'sort': sort, 'amount_filter': amount_filter}
    return render(request, 'users_temp/categories.html', context)




#Notice
def notice(request):
    return render(request, 'users_temp/notice.html')
    


#Profile
@login_required(login_url='/accounts/login_user/')
def profile(request):
    if 'email' in request.session:
        user = request.user
        tokens = Token.objects.filter(owner=user)
        wallet = Wallet.objects.filter(user=user).first()
        total_token = tokens.count()
        context = {'tokens': tokens, 'total_token': total_token, 'wallet': wallet}
        return render(request, 'users_temp/profile.html', context)
    else:
        return redirect('/')
    


#Created tokens profile
@login_required(login_url='/accounts/login_user/')
def profile_created(request):
    if 'email' in request.session:
        user = request.user
        wallet = Wallet.objects.filter(user=user).first()
        tokens = Token.objects.filter(author=user)
        total_token = tokens.count()
        context = {'tokens': tokens, 'total_token': total_token, 'wallet': wallet}
        return render(request, 'users_temp/profile.html', context)
    else:
        return redirect('/')



#Edit Profile
@login_required(login_url='/accounts/login_user/')
def edit_profile(request):
    user = request.user
    form = Profileform(instance=user)

    if request.method == 'POST':
        form = Profileform(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            user = form.save(commit=False)
            user.save()
            messages.success(request, 'Success!! Your profile has been updated successfully.')
            return redirect('edit_profile')
        else:
            print(form.errors)
            messages.error(request, 'There was an error updating your profile.')
    
    context = {'user': user, 'form': form}
    return render(request, 'users_temp/edit-profile.html', context)



#Remove profile
@login_required(login_url='/accounts/login_user/')
def remove_profile(request, user_id):
    account = Account.objects.get(id=user_id)
    account.profile_pic = settings.MEDIA_ROOT + '/profile.png'
    account.save()
    messages.success(request, 'Oops! your profile picture removed')
    return redirect(edit_profile)



#Recharge Wallet
razorpay_client = Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required(login_url='/accounts/login_user/')
def wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    user = request.user
    context = {'user': user, 'wallet': wallet}
    return render(request, 'users_temp/wallet.html', context)



#Adding fund to Wallet
@csrf_exempt
@login_required(login_url='/accounts/login_user/')
def add_funds(request):
    user_wallet, created = Wallet.objects.get_or_create(user=request.user)
    if created:
        user_wallet.save()
    if request.method == 'POST':
        amount = int(request.POST['amount']) * 100
        razorpay_order = razorpay_client.order.create({'amount': amount, 'currency': 'INR'})
        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount,
        }
        user_wallet.razor_pay_order_id = razorpay_order['id']
        user_wallet.save()
        return render(request, 'users_temp/razorpay.html', context)
    return redirect('wallet')



#Payment Success
@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        data = request.POST
        try:
            razorpay_client.utility.verify_payment_signature(data)
            order_id = data.get('razorpay_order_id')
            wallet = Wallet.objects.get(razor_pay_order_id=order_id)
            user_wallet = wallet.user.wallet_obj
            amount = str(int(data['amount']) / 100)
            user_wallet.balance += decimal.Decimal(amount)
            user_wallet.transaction_history.append(f"Recharged amount {amount}")
            user_wallet.razor_pay_payment_id = data.get('razorpay_payment_id')
            user_wallet.razor_pay_signature = data.get('razorpay_signature')
            user_wallet.save()
            messages.success(request, 'Payment successful')
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, 'Invalid payment signature')
        except Wallet.DoesNotExist:
            messages.error(request, f'Wallet not found for order id: {order_id}')
        except Exception as e:
            messages.error(request, f'Payment failed: {str(e)}')

    return redirect('wallet')



#Redeem from wallet
def redeem(request):
    if request.method == 'POST':
        amount = int(request.POST['amount'])
        user_wallet = request.user.wallet_obj
        if user_wallet.balance >= amount:
            # Deduct amount from wallet balance
            user_wallet.balance -= amount
            user_wallet.transaction_history.append(f"Amount Redeemed from the wallet is ₹{amount}")
            user_wallet.save()

            # Initiate refund using Razorpay API
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            refund = client.payment.refund(user_wallet.razor_pay_payment_id, {"amount": amount*100})

            messages.success(request, f"{amount} INR has been redeemed to your account.")
            return redirect('redeem')

        else:
            messages.error(request, f"You do not have sufficient balance to redeem {amount} INR.")
        return redirect('redeem')

    return render(request, 'users_temp/redeem.html')



#Cart
@login_required(login_url='/accounts/login_user/')
def cart(request):
    cart_owner = request.user
    cart = Cart.objects.filter(cart_owner=cart_owner, submitted=False).first()
    cart_items = CartItems.objects.filter(account=cart_owner).select_related('cart_items')
    items_count = cart_items.count()
    
    # total price
    if not cart_items.exists():
        total_price = 0
        if cart:
            cart.total_price = 0
            cart.save()
    else:
        total_price = cart.total_price if cart else 0
       
    context = {
        'cart_owner': cart_owner,
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
        'items_count': items_count,
    }
    return render(request,'users_temp/cart.html',context)



#Add to Cart
@login_required(login_url='/accounts/login_user/')
def addtocart(request, id):
    token = get_object_or_404(Token, id=id)
    user = request.user
    cart, created = Cart.objects.get_or_create(cart_owner=user, submitted=False)
    cart_item, created = CartItems.objects.get_or_create(cart_items=token, account=user)
    cart_item.save()
    if created:
        cart.total_price += token.price
    cart.save()
    if created:
        messages.success(request, 'Added to cart successfully')
    return redirect('items')



#Remove item from cart
def remove_item(request, id):
    cart_owner = request.user
    cart = Cart.objects.filter(cart_owner=cart_owner, submitted=False).first()
    cart_item = CartItems.objects.get(id=id)
    if cart_item:
        cart.total_price -= cart_item.cart_items.price
        cart_item.delete()
        cart_items = CartItems.objects.filter(account=cart_owner)
        if not cart_items.exists():
            cart.total_price = 0
        cart.save()
    return redirect('cart')

        

#Checkout
@login_required(login_url='/accounts/login_user/')
def checkout(request):
    user = request.user
    cart_items = CartItems.objects.filter(account=user)
    items_count = cart_items.count()
    total_price = sum(item.cart_items.price for item in cart_items)
    commission = round(total_price * 0.035, 2)
    total = total_price + commission

    context = {'cart_items': cart_items, 'items_count': items_count, 'total_price': total_price, 'commission': commission, 'total': total}
    return render(request, 'users_temp/checkout.html', context)



#Create
@login_required(login_url='/accounts/login_user/')
def create(request):
    if 'email' or 'super_email' in request.session:
        user_id = request.user.id
        user = Account.objects.get(id=user_id)
        if request.method == 'POST':
            form = TokenForm(request.POST, request.FILES)
            if form.is_valid():
                token = form.save(commit=False)
                token.owner = user
                token.author = user
                token.save()
                messages.info(request, 'Token Created successfully')
                return redirect('create')
        else:
            form = TokenForm()
        context = {'form': form, 'user': user, 'user_id': user_id}
    else:
        return redirect('home')
    return render(request, 'users_temp/create.html', context)



#Single view of tokens
def single_item(request, id):
    product = Token.objects.get(id=id)
    context = {'product': product}
    return render(request, 'users_temp/single-item.html', context)



#Cancel Sale
@login_required(login_url='/accounts/login_user/')
def cancel_sale(request, id):
    token = Token.objects.get(id=id)
    token.is_active = False
    token.save()
    return redirect('single_item', id=id)



#Edit Token
@login_required(login_url='/accounts/login_user/')
def edit_token(request, id):
    product = Token.objects.get(id=id)
    form = TokenForm(instance=product)

    if request.method == 'POST':
        form = TokenForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Success!! your Token is updated successfully')
            return redirect('edit_token', id=id)
        else:
            print(form.errors)  # add this line to print form errors
            messages.error(request, 'There was an error updating your token')

    context = {'product': product, 'form': form}
    return render(request, 'users_temp/edit-token.html', context)



#Sell the token
@login_required(login_url='/accounts/login_user/')
def sell(request, id):
    token = Token.objects.get(id=id)
    token.is_active = True
    token.save()
    return redirect('single_item', id=id)



#Like token
@login_required(login_url='/accounts/login_user/')
def like(request, id):
    user = request.user
    token = Token.objects.get(id=id)
    liked_product, created = Like.objects.get_or_create(likes=True, owner=user, token=token)
    if created:
        token.likes_count += 1
        token.save()
    return redirect(request.META.get('HTTP_REFERER'))



# Dislike token
@login_required(login_url='/accounts/login_user/')
def dislike(request, id):
    user = request.user
    token = Token.objects.get(id=id)
    liked_product = Like.objects.filter(likes=True, owner=user, token=token).first()
    if liked_product:
        liked_product.delete()
        token.likes_count -= 1
        token.save()
    return redirect(request.META.get('HTTP_REFERER'))



#Single Purchase
@login_required(login_url='/accounts/login_user/')
def checkout_single(request, id):
    user = request.user
    token = Token.objects.get(id=id)

    price = token.price
    commission = round(price * 0.035, 2)
    total = price + commission

    context = {'token': token, 'user': user, 'price': price, 'commission': commission, 'total': total}
    return render(request, 'users_temp/checkout-single.html', context)



#Base
def base(request):
    user = Account.objects.all()
    context = {'user': user}
    return render(request, 'users_temp/base.html', context)



#Complete Transaction
def complete_transaction(request, id):
    user = request.user
    token = Token.objects.filter(id=id).first()
    wallet = Wallet.objects.get(user=user)
    if request.method == 'POST':
        total = Decimal(request.POST['total'])
        commission = Decimal(request.POST['commission'])
        if total > wallet.balance:
            messages.error(request, 'Wallet does not have enough balance to complete this transaction.')
            return redirect('complete_transaction', id=id)
        else:
            # Update token ownership and is_active status
            if total >= token.price:
                # Update wallets
                user_wallet = Wallet.objects.get(user=request.user)
                user_wallet.balance -= total
                user_wallet.transaction_history.append(f"Paid {total} for token '{token.name}'")
                user_wallet.save()

                owner_wallet = Wallet.objects.get(user=token.owner)
                owner_wallet.balance += Decimal(str(token.price))
                owner_wallet.transaction_history.append(f"Received {token.price} for token '{token.name}' from {user}")
                owner_wallet.save()

                token.is_active = False
                token.owner = user
                token.save()

                # Convert commission to decimal.Decimal before adding to superuser_wallet balance
                commission_decimal = Decimal(str(commission))
                superuser_wallet = Wallet.objects.filter(user__is_superadmin=True).first()
                if superuser_wallet:
                    superuser_wallet.balance += commission_decimal
                    superuser_wallet.transaction_history.append(f"Received {commission_decimal} commission from {user} for token '{token.name}'")
                    superuser_wallet.save()

            else:
                messages.error(request, f'Total amount {total} is less than the price of the token {token.price}.')
                return redirect('complete_transaction', id=id)

            messages.success(request, f'Transaction successful. You are now the owner of token {token.name}.')
            return redirect('single_item', id=id)
    else:
        price = token.price
        commission = round(price * 0.035, 2)
        total = price + commission
        return render(request, 'users_temp/checkout-single.html', {'token': token, 'total': total, 'commission': commission})



#Complete Transaction of checkout
def checkout_complete_transaction(request):
    user = request.user
    cart_items = CartItems.objects.filter(account=user)
    wallet = Wallet.objects.get(user=user)
    if request.method == 'POST':
        total = Decimal(request.POST['total'])
        commission = Decimal(request.POST['commission'])
        total_price = Decimal(request.POST['total_price'])
        if total > wallet.balance:
            messages.error(request, 'Wallet does not have enough balance to complete this transaction.')
            return redirect('checkout_complete_transaction')
        else:
            if total >= total_price:
                # Update wallets
                user_wallet = Wallet.objects.get(user=request.user)
                user_wallet.balance -= total
                user_wallet.transaction_history.append(f"Paid {total} for cart items")
                user_wallet.save()

                # Add commission to superuser_wallet balance
                commission_decimal = Decimal(str(commission))
                superuser_wallet = Wallet.objects.filter(user__is_superadmin=True).first()
                if superuser_wallet:
                    superuser_wallet.balance += commission_decimal
                    superuser_wallet.transaction_history.append(f"Received {commission_decimal} commission from {user} for cart purchase")
                    superuser_wallet.save()

                # Update owner's wallet and set ownership of tokens
                for item in cart_items:
                    owner_wallet = Wallet.objects.get(user=item.cart_items.owner)
                    owner_wallet.balance += Decimal(str(item.cart_items.price))
                    owner_wallet.transaction_history.append(f"Received {item.cart_items.price} for token '{item.cart_items.name}' from {user}")
                    owner_wallet.save()

                    item.cart_items.is_active = False
                    item.cart_items.owner = user
                    item.cart_items.save()
                    # Delete purchased items from the cart
                    cart = Cart.objects.filter(cart_owner=user, submitted=False).first()
                    if cart:
                        for item in cart_items:
                            item.delete()

                        cart.total_price = 0
                        cart.save()

            else:
                messages.error(request, f'Total amount {total} is less than the price of the tokens in the cart.')
                return redirect('checkout_complete_transaction')

            messages.success(request, f'Transaction successful. You are now the owner of tokens stored in the cart.')
            return redirect('cart')
    else:
        total_price = sum(item.cart_items.price for item in cart_items)
        commission = round(total_price * 0.035, 2)
        total = total_price + commission
        return render(request, 'users_temp/checkout.html', {'cart_items': cart_items, 'total': total, 'commission': commission})
