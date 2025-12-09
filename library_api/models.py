from django.db import models
from django.conf import settings
from django.utils import timezone
import os


class AuthorAPI(models.Model):
    """
    Модель автора для API (расширенная версия)
    """
    name = models.CharField(max_length=150, unique=True)
    biography = models.TextField(blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Author (API)'
        verbose_name_plural = 'Authors (API)'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def books_count(self):
        return self.books.count()


class BookAPI(models.Model):
    """
    Модель книги для API с уникальными ограничениями
    """
    CATEGORY_CHOICES = [
        ('fiction', 'Художественная литература'),
        ('textbook', 'Учебник'),
        ('science', 'Научная литература'),
        ('business', 'Бизнес-литература'),
        ('other', 'Другое'),
    ]

    title = models.CharField(max_length=100)
    author = models.ForeignKey(AuthorAPI, on_delete=models.CASCADE, related_name='books')
    publication_year = models.IntegerField()
    genre = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='fiction')
    publisher = models.CharField(max_length=100)

    # Поля для файлов
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    book_file = models.FileField(upload_to='books/', blank=True, null=True)

    # Дополнительные поля
    is_textbook = models.BooleanField(default=False)
    edition = models.IntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)

    # Метаданные
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Book (API)'
        verbose_name_plural = 'Books (API)'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author', 'publication_year', 'publisher'],
                name='unique_book_api'
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.author.name})"

    def clean(self):
        """
        Валидация при сохранении
        """
        from django.core.exceptions import ValidationError

        # Проверка года публикации
        if self.publication_year < 1000 or self.publication_year > 9999:
            raise ValidationError({'publication_year': 'Year must be between 1000 and 9999'})

        # Проверка для учебников
        if self.is_textbook and self.edition < 1:
            raise ValidationError({'edition': 'Edition must be at least 1 for textbooks'})

    def save(self, *args, **kwargs):
        self.full_clean()  # Вызов валидации
        super().save(*args, **kwargs)

    @property
    def file_size(self):
        """Возвращает размер файла книги"""
        if self.book_file and hasattr(self.book_file, 'size'):
            size = self.book_file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return None