import uuid
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Wallet"
    
    @property
    def balance(self):
        deposits = self.transactions.filter(transaction_type='deposit').aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        withdrawals = self.transactions.filter(transaction_type='withdrawal').aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        return deposits - withdrawals

    def apply_transaction(self, transaction_type, amount):
        if transaction_type == 'withdrawal' and self.balance < amount:
            raise ValueError("Insufficient balance")

        with transaction.atomic():
            WalletTransaction.objects.create(
                wallet=self,
                transaction_type=transaction_type,
                amount=amount
            )

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
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