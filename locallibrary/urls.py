
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static

from catalog import views

#Add Django site authentication urls (for login, logout, password management)
# Инициализируем urlpatterns как пустой список
urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalog/', include('catalog.urls')),
    path('catalog/', include('catalog.urls')),
    path('accounts/', include('django.contrib.auth.urls')),



]

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