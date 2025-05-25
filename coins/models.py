import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Coin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)

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