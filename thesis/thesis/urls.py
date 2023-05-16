from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.urls import include
from django.urls import re_path as url
from django.conf.urls.static import static
from thesisapp.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('thesisapp.urls')),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('password_reset/done/', MyPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', MyPasswordResetCompleteView.as_view(), name='password_reset_complete'),


    url(r'^', include('thesisapp.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)