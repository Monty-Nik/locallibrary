from . import views
from django.urls import path
from django.urls import re_path

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^books/$', views.BookListView.as_view(), name='books'),
    re_path(r'^book/(?P<pk>\d+)$', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),  # имя 'authors' для списка авторов
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('author-list/', views.AuthorListView.as_view(), name='author_list'),
]
urlpatterns += [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
]

urlpatterns += [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('profile/', views.profile_view, name='profile'),  # добавьте этот путь
]

urlpatterns += [
    re_path(r'^mybooks/$', views.LoanedBooksByUserListView, name='my-borrowed'),
    re_path(r'^all-borrowed/$', views.AllLoanedBooksListView.as_view(), name='all-borrowed'),
]