from rest_framework import serializers
from .models import AuthorAPI, BookAPI
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AnonymousUser

class AuthorAPISerializer(serializers.ModelSerializer):
    """Сериализатор для авторов"""
    books_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = AuthorAPI
        fields = [
            'id', 'name', 'biography', 'birth_date',
            'death_date', 'nationality', 'books_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class BookAPISerializer(serializers.ModelSerializer):
    """Сериализатор для книг"""
    author_name = serializers.CharField(source='author.name', read_only=True)
    file_size = serializers.CharField(read_only=True)

    class Meta:
        model = BookAPI
        fields = [
            'id', 'title', 'author', 'author_name',
            'publication_year', 'genre', 'category',
            'publisher', 'cover_image', 'book_file',
            'is_textbook', 'edition', 'description',
            'isbn', 'file_size', 'created_at', 'updated_at',
            'created_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def validate(self, data):
        """Кастомная валидация"""
        # Проверка года публикации
        if 'publication_year' in data:
            year = data['publication_year']
            if year < 1000 or year > 9999:
                raise serializers.ValidationError({
                    'publication_year': 'Year must be between 1000 and 9999'
                })

        # Проверка уникальности
        if BookAPI.objects.filter(
                title=data.get('title'),
                author=data.get('author'),
                publication_year=data.get('publication_year'),
                publisher=data.get('publisher')
        ).exists():
            raise serializers.ValidationError({
                'non_field_errors': ['Book with these details already exists']
            })

        return data

    def create(self, validated_data):
        """Переопределение создания для установки создателя"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
        if not isinstance(user, AnonymousUser) and user.is_authenticated:
            validated_data['created_by'] = user

        return super().create(validated_data)


class BookSearchSerializer(serializers.Serializer):
    """Сериализатор для поиска"""
    q = serializers.CharField(required=True)
    search_by = serializers.ChoiceField(
        choices=['title', 'genre', 'author'],
        default='title'
    )


class FileUploadSerializer(serializers.Serializer):
    """Сериализатор для загрузки файлов"""
    file = serializers.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'epub', 'txt'])]
    )