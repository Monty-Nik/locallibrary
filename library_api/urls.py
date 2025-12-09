from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'authors', views.AuthorAPIViewSet, basename='author-api')
router.register(r'books', views.BookAPIViewSet, basename='book-api')

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('stats/', views.StatisticsView.as_view(), name='api-stats'),
    path('', include(router.urls)),
]