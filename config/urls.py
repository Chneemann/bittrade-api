from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from users.views import LoginView, MeView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Auth
    path('auth/me/', MeView.as_view(), name='me'),
    path('auth/login/', LoginView.as_view(), name='login'),

    # Favicon
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)