from django.apps import apps
from django.db import models
from django.contrib.postgres.fields import ArrayField

def get_account_model():
    return apps.get_model('admins', 'Category')

def get_account_model():
    return apps.get_model('accounts', 'Account')


class Token(models.Model):
    name = models.CharField(max_length=200, null=True)
    description = models.TextField()
    price = models.FloatField()
    brand = models.CharField(max_length=100, null=True)
    image = models.ImageField(null=True, blank=True)
    likes_count = models.FloatField(default=0)
    category = models.ForeignKey('admins.Category', on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    author = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='token_author', null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class Like(models.Model):
    owner = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='likes')
    likes = models.BooleanField(default=False)
    

class Cart(models.Model):
    cart_owner = models.ForeignKey('accounts.Account', on_delete=models.SET_NULL, blank=True, null=True)
    submitted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    total_price = models.FloatField(default=0)

    def __str__(self):
        return str(self.id)
    

class CartItems(models.Model):
    cart_items = models.ForeignKey(Token, on_delete=models.SET_NULL, blank=True, null=True, related_name='cart_items')
    account = models.ForeignKey('accounts.Account', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.id)



class Payments(models.Model):
    amount = models.FloatField(blank=True, null=True)
    sold = models.BooleanField(default=False, null=True, blank=False)
    method = models.CharField(max_length=200, default='Razorpay')
    timestamp = models.DateTimeField(auto_now_add=True)
    razor_pay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_signature = models.CharField(max_length=100, null=True, blank=True)
    customer = models.ForeignKey('accounts.Account', on_delete=models.SET_NULL,  blank=True, null=True)

    def __str__(self):
        return str(self.id)



class Wallet(models.Model):
    user = models.OneToOneField('accounts.Account', on_delete=models.CASCADE, related_name='wallet_obj')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_history = ArrayField(models.CharField(max_length=100), default=list)
    razor_pay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_signature = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.id)