from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import AuthorAPI, BookAPI
from .serializers import (
    AuthorAPISerializer, BookAPISerializer,
    BookSearchSerializer, FileUploadSerializer
)
from .permissions import IsAdminOrReadOnly


class AuthorAPIViewSet(viewsets.ModelViewSet):
    queryset = AuthorAPI.objects.all().order_by('name')
    serializer_class = AuthorAPISerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'nationality']

    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        author = self.get_object()
        books = author.books.all()
        serializer = BookAPISerializer(books, many=True)
        return Response(serializer.data)


class BookAPIViewSet(viewsets.ModelViewSet):
    queryset = BookAPI.objects.all().order_by('-created_at')
    serializer_class = BookAPISerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_textbook', 'genre']
    search_fields = ['title', 'author__name', 'genre', 'publisher']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def search(self, request):
        serializer = BookSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        query = serializer.validated_data['q']
        search_by = serializer.validated_data['search_by']

        if search_by == 'title':
            books = BookAPI.objects.filter(title__icontains=query)
        elif search_by == 'genre':
            books = BookAPI.objects.filter(genre__icontains=query)
        elif search_by == 'author':
            books = BookAPI.objects.filter(author__name__icontains=query)
        else:
            books = BookAPI.objects.filter(
                Q(title__icontains=query) |
                Q(genre__icontains=query) |
                Q(author__name__icontains=query)
            )

        page = self.paginate_queryset(books)
        if page is not None:
            serializer = BookAPISerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BookAPISerializer(books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def textbooks(self, request):
        textbooks = BookAPI.objects.filter(is_textbook=True)
        serializer = self.get_serializer(textbooks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        recent_books = BookAPI.objects.all().order_by('-created_at')[:10]
        serializer = self.get_serializer(recent_books, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'authors': request.build_absolute_uri('/api/v1/authors/'),
        'books': request.build_absolute_uri('/api/v1/books/'),
        'search': request.build_absolute_uri('/api/v1/books/search/'),
        'textbooks': request.build_absolute_uri('/api/v1/books/textbooks/'),
        'recent': request.build_absolute_uri('/api/v1/books/recent/'),
    })


class StatisticsView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        stats = {
            'total_books': BookAPI.objects.count(),
            'total_authors': AuthorAPI.objects.count(),
            'textbooks_count': BookAPI.objects.filter(is_textbook=True).count(),
            'categories': {
                category[0]: BookAPI.objects.filter(category=category[0]).count()
                for category in BookAPI.CATEGORY_CHOICES
            }
        }
        return Response(stats)