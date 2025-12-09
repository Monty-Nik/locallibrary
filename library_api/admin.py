from django.contrib import admin
from .models import AuthorAPI, BookAPI


@admin.register(AuthorAPI)
class AuthorAPIAdmin(admin.ModelAdmin):
    list_display = ['name', 'nationality', 'books_count', 'created_at']
    list_filter = ['nationality', 'created_at']
    search_fields = ['name', 'biography']
    ordering = ['name']

    def books_count(self, obj):
        return obj.books.count()

    books_count.short_description = 'Книги'


@admin.register(BookAPI)
class BookAPIAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_textbook', 'publication_year', 'created_at']
    list_filter = ['category', 'is_textbook', 'genre', 'created_at']
    search_fields = ['title', 'author__name', 'isbn']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'author', 'publication_year', 'isbn')
        }),
        ('Классификация', {
            'fields': ('genre', 'category', 'is_textbook', 'edition')
        }),
        ('Дополнительно', {
            'fields': ('publisher', 'description', 'cover_image', 'book_file')
        }),
        ('Метаданные', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)