from rest_framework import serializers
from .models import Cat, Category
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
