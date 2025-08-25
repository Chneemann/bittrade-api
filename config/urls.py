from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from users.views import LoginView, LogoutView, MeView, MeUpdateView, PasswordResetConfirmView, RegisterView, PasswordResetRequestView, ConfirmEmailView
from wallets.views import MyWalletView, DepositWalletView, WithdrawWalletView, WalletTransactionsView
from coins.views import CoinView, MyCoinTransactionView, MyCoinTransactionsView, MyCoinHoldingView, MyCoinHoldingsView
from caches.views import QueueCoinCacheView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Auth
    path('auth/me/', MeView.as_view(), name='me'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='request-password-reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='confirm-password-reset'),
    path('auth/verify-email/', ConfirmEmailView.as_view(), name='verify-email'),

    # Profile
    path('auth/me/update/', MeUpdateView.as_view(), name='me-update'),
    
    # user coins
    path('api/me/coin/transactions/', MyCoinTransactionsView.as_view(), name='my-coin-transactions'),
    path('api/me/coin/transaction/<str:coin_id>/', MyCoinTransactionView.as_view(), name='my-coin-transaction'),
    path('api/me/coin/holdings/', MyCoinHoldingsView.as_view(), name='my-coin-holdings'),
    path('api/me/coin/holding/<str:coin_id>/', MyCoinHoldingView.as_view(), name='my-coin-holding'),
    
    #user wallet
    path('api/me/wallet/', MyWalletView.as_view(), name='my-wallet'),
    path('api/me/wallet/transactions/', WalletTransactionsView.as_view(), name='my-wallet-transactions'),
    path('api/me/wallet/transactions/<str:source>/', WalletTransactionsView.as_view(), name='my-wallet-transactions'),
    path('api/me/wallet/deposit/', DepositWalletView.as_view(), name='my-wallet-deposit'),
    path('api/me/wallet/withdraw/', WithdrawWalletView.as_view(), name='my-wallet-withdraw'),

    # coins
    path('api/coins/', CoinView.as_view(), name='coins'),

    # coins cache
    path("api/coins/queue-cache/", QueueCoinCacheView.as_view(), name="queue-coin-cache"),
    
    # Favicon
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)