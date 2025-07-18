import uuid
from django.db import models, transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.conf import settings


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s Wallet"
    
    @property
    def current_balance(self):
        deposits = self.transactions.filter(transaction_type='deposit').aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        withdrawals = self.transactions.filter(transaction_type='withdrawal').aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        return deposits - withdrawals

    def apply_transaction(self, transaction_type, amount, transaction_source):
        if transaction_type not in dict(WalletTransaction.TRANSACTION_TYPES):
            raise ValueError("Invalid transaction type")
        if transaction_source not in dict(WalletTransaction.TRANSACTION_SOURCES):
            raise ValueError("Invalid transaction source")
        if transaction_type == 'withdrawal' and self.current_balance < amount:
            raise ValueError("Insufficient balance")
        
        with transaction.atomic():
            WalletTransaction.objects.create(
                wallet=self,
                transaction_type=transaction_type,
                transaction_source=transaction_source,
                amount=amount.quantize(Decimal('0.01'))
            )

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]

    TRANSACTION_SOURCES = [
        ('fiat', 'Fiat Transfer'),
        ('coin', 'Coin Trade'), 
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    transaction_source = models.CharField(max_length=20, choices=TRANSACTION_SOURCES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
    
    def __str__(self):
        return f"{self.wallet.user.username} {self.transaction_type} {self.amount}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError({'amount': "Amount must be greater than zero."})

        transactions = WalletTransaction.objects.filter(wallet=self.wallet)
        if self.pk:
            transactions = transactions.exclude(pk=self.pk)

        deposits = transactions.filter(transaction_type='deposit').aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        withdrawals = transactions.filter(transaction_type='withdrawal').aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

        if self.transaction_type == 'deposit':
            deposits += self.amount
        else:
            withdrawals += self.amount

        if deposits - withdrawals < 0:
            raise ValidationError({'amount': "Insufficient funds after this transaction."})
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)