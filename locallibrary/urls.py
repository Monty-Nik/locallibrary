from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from catalog import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalog/', include('catalog.urls')),
    path('catalog/', include('catalog.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/v1/', include('library_api.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Затем добавляем аутентификацию
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]


from django.views.generic import RedirectView
urlpatterns += [
    path('', RedirectView.as_view(url='catalog/', permanent=True)),
    path('all-borrowed/', views.AllBorrowedBooksListView.as_view(), name='all-borrowed'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)