from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('teams/', include('teams.urls')),
    path('health-cards/', include('health_cards.urls')),
    path('votes/', include('votes.urls')),
    path('summaries/', include('summaries.urls')),
    path('', include('accounts.urls')),  # Default to accounts URLs for the root path
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
