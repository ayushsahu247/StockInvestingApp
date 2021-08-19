from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.db.models.deletion import CASCADE
# Create your models here.

class Investor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField( max_digits=10 ,decimal_places=2, default=100000)

    def __str__(self):
        return str(self.user.username)

class Stock(models.Model):
    symbol = models.CharField(max_length=50)
    companyName = models.CharField(max_length=150)

    def __str__(self):
        return self.symbol


class Investment(models.Model):
    investor = models.ForeignKey(Investor, on_delete=CASCADE)
    stock = models.ForeignKey(Stock, on_delete=CASCADE)
    n_shares = models.IntegerField()
    avg_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.investor.user.username + '-'+self.stock.symbol


class Record(models.Model):
    investor = models.ForeignKey(Investor, on_delete=CASCADE)
    stock = models.ForeignKey(Stock, on_delete=CASCADE)
    message = models.CharField(max_length=1000)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.investor.user.username + '-'+self.stock.symbol