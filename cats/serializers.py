from rest_framework import serializers
from .models import Cat, Category, Collection, CollectionItem
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CatSerializer(serializers.ModelSerializer):
    def validate_birth_year(self, value):
        import datetime
        if value > datetime.date.today().year:
            raise serializers.ValidationError("Год рождения не может быть в будущем!")
        return value

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Имя не может быть пустым!")
        return value

    class Meta:
        model = Cat
        fields = '__all__'
        read_only_fields = ['owner']


class CollectionItemSerializer(serializers.ModelSerializer):
    cat = CatSerializer(read_only=True)
    cat_id = serializers.PrimaryKeyRelatedField(queryset=Cat.objects.all(), source='cat', write_only=True)

    class Meta:
        model = CollectionItem
        fields = ['id', 'cat', 'cat_id', 'added_at']
        read_only_fields = ['added_at']


class CollectionSerializer(serializers.ModelSerializer):
    items = CollectionItemSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'name', 'description', 'is_private', 'owner', 'owner_name', 'created_at', 'items']
        read_only_fields = ['owner', 'created_at']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Название подборки не может быть пустым!")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request and request.method == 'POST':
            if Collection.objects.filter(owner=request.user, name=data['name']).exists():
                raise serializers.ValidationError({"name": "Подборка с таким именем уже существует у владельца."})
        return data
