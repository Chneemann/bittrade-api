import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum, F, DecimalField
from django.utils.text import slugify
from decimal import Decimal

User = get_user_model()

class Coin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10, unique=True)
    slug = models.SlugField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.symbol})"
    
class CoinHolding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    average_buy_price = models.DecimalField(max_digits=20, decimal_places=8, default=0)

    class Meta:
        verbose_name = "Holding"
        verbose_name_plural = "Holdings"
        constraints = [
            models.UniqueConstraint(fields=['user', 'coin'], name='unique_user_coin')
        ]

    def __str__(self):
        return f"{str(self.user)} - {self.coin.symbol}: {self.amount}"

class CoinTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE, limit_choices_to={'is_active': True})
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    price_per_coin = models.DecimalField(max_digits=20, decimal_places=8)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        
    def __str__(self):
        type_display = dict(self.TRANSACTION_TYPES).get(self.transaction_type, self.transaction_type)
        return f"{self.user} {type_display} {self.amount} {self.coin.symbol}"

    @staticmethod
    def update_user_holding(user, coin):
        transactions = CoinTransaction.objects.filter(user=user, coin=coin)

        total_bought_amount = transactions.filter(transaction_type='buy').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')

        total_sold_amount = transactions.filter(transaction_type='sell').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')

        total_bought_cost = transactions.filter(transaction_type='buy').aggregate(
            total=Sum(F('amount') * F('price_per_coin'), output_field=DecimalField())
        )['total'] or Decimal('0')

        total_amount = total_bought_amount - total_sold_amount

        if total_amount > 0:
            average_buy_price = total_bought_cost / total_bought_amount
        else:
            average_buy_price = Decimal('0')

        holding, _ = CoinHolding.objects.get_or_create(user=user, coin=coin)
        holding.amount = total_amount
        holding.average_buy_price = average_buy_price
        holding.save()

    def clean(self):
        if self.amount <= 0:
            raise ValidationError({'amount': "Amount must be greater than zero."})
        if self.price_per_coin <= 0:
            raise ValidationError({'price_per_coin': "Price per coin must be greater than zero."})

        if self.transaction_type == 'sell':
            transactions = CoinTransaction.objects.filter(user=self.user, coin=self.coin)
            if self.pk:
                transactions = transactions.exclude(pk=self.pk)

            total_bought = transactions.filter(transaction_type='buy').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
            total_sold = transactions.filter(transaction_type='sell').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
            current_amount = total_bought - total_sold

            if self.amount > current_amount:
                raise ValidationError({
                    'amount': f"Not enough stock: You only have {current_amount:.8f} {self.coin.symbol}, "
                              f"but would like to sell {self.amount:.8f}."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.update_user_holding(self.user, self.coin)

    def delete(self, *args, **kwargs):
        user, coin = self.user, self.coin
        super().delete(*args, **kwargs)
        self.update_user_holding(user, coin)