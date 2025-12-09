from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import AuthorAPI, BookAPI
import tempfile
from PIL import Image


class AuthorAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)

        self.author = AuthorAPI.objects.create(
            name='Тестовый Автор',
            nationality='Русский'
        )

    def test_get_authors_list(self):
        url = reverse('author-api-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_author(self):
        url = reverse('author-api-list')
        data = {
            'name': 'Новый Автор',
            'nationality': 'Английский'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AuthorAPI.objects.count(), 2)


class BookAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)

        self.author = AuthorAPI.objects.create(
            name='Тестовый Автор'
        )

        self.book = BookAPI.objects.create(
            title='Тестовая Книга',
            author=self.author,
            publication_year=2023,
            publisher='Тестовое Издательство',
            isbn='978-1234567890'
        )

    def test_get_books_list(self):
        url = reverse('book-api-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_books(self):
        url = reverse('book-api-list') + 'search/?q=Тест&search_by=title'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book_validation(self):
        url = reverse('book-api-list')
        data = {
            'title': 'Тестовая Книга',
            'author': self.author.id,
            'publication_year': 2023,
            'publisher': 'Тестовое Издательство',
        }
        response = self.client.post(url, data, format='json')
        # Должна быть ошибка, потому что такая книга уже есть
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)