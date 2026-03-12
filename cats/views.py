from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Cat, Category, Collection, CollectionItem
from .serializers import CatSerializer, CategorySerializer, CollectionSerializer, CollectionItemSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if isinstance(obj, Collection):
                if obj.is_private and obj.owner != request.user:
                    return False
                return True
            return True
        return obj.owner == request.user


class IsCollectionOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if obj.collection.is_private and obj.collection.owner != request.user:
                return False
            return True
        return obj.collection.owner == request.user


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Cat.objects.filter(
                models.Q(owner=user) | models.Q(collection_items__collection__is_private=False)
            ).distinct()
        return Cat.objects.filter(collection_items__collection__is_private=False).distinct()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CollectionViewSet(viewsets.ModelViewSet):
    # Добавлен queryset для исправления ошибки роутера
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Collection.objects.filter(
                models.Q(is_private=False) | models.Q(owner=user)
            )
        return Collection.objects.filter(is_private=False)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], url_path='add-cat')
    def add_cat(self, request, pk=None):
        collection = self.get_object()
        if collection.owner != request.user:
            return Response({"detail": "Только владелец может добавлять котов в подборку."},
                            status=status.HTTP_403_FORBIDDEN)

        cat_id = request.data.get('cat_id')
        if not cat_id:
            return Response({"detail": "Не указан ID кота."}, status=status.HTTP_400_BAD_REQUEST)

        cat = get_object_or_404(Cat, id=cat_id)

        if CollectionItem.objects.filter(collection=collection, cat=cat).exists():
            return Response({"detail": "Этот кот уже есть в подборке."}, status=status.HTTP_400_BAD_REQUEST)

        CollectionItem.objects.create(collection=collection, cat=cat)
        return Response({"detail": "Кот успешно добавлен в подборку."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='remove-cat')
    def remove_cat(self, request, pk=None):
        collection = self.get_object()
        if collection.owner != request.user:
            return Response({"detail": "Только владелец может удалять котов из подборки."},
                            status=status.HTTP_403_FORBIDDEN)

        cat_id = request.data.get('cat_id')
        if not cat_id:
            return Response({"detail": "Не указан ID кота."}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(CollectionItem, collection=collection, cat_id=cat_id)
        item.delete()
        return Response({"detail": "Кот успешно удален из подборки."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='my-collections')
    def my_collections(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Требуется авторизация."}, status=status.HTTP_401_UNAUTHORIZED)
        queryset = Collection.objects.filter(owner=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
