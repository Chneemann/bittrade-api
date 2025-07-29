from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from users.views import LoginView, LogoutView, MeView, MeUpdateView, RegisterView, PasswordResetRequestView, MyTransactionsView, MyCoinTransactionsView, MyHoldingsView, MyCoinHoldingsView, ConfirmEmailView
from wallets.views import MyWalletView, DepositWalletView, WithdrawWalletView
from coins.views import CoinView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Auth
    path('auth/me/', MeView.as_view(), name='me'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='request-password-reset'),
    path('auth/verify-email/', ConfirmEmailView.as_view(), name='verify-email'),

    # Profile
    path('auth/me/update/', MeUpdateView.as_view(), name='me-update'),
    
    # user coins
    path('api/me/transactions/', MyTransactionsView.as_view(), name='my-transactions'),
    path('api/me/transactions/<str:coin_id>/', MyCoinTransactionsView.as_view(), name='my-coin-transactions'),
    path('api/me/holdings/', MyHoldingsView.as_view(), name='my-holdings'),
    path('api/me/holdings/<str:coin_id>/', MyCoinHoldingsView.as_view(), name='my-holdings'),
    
    #user wallet
    path('api/me/wallet/', MyWalletView.as_view(), name='my-wallet'),
    path('api/me/wallet/deposit/', DepositWalletView.as_view(), name='my-wallet-deposit'),
    path('api/me/wallet/withdraw/', WithdrawWalletView.as_view(), name='my-wallet-withdraw'),

    # coins
    path('api/coins/', CoinView.as_view(), name='coins'),

    # Favicon
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)