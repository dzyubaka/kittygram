from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Cat(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cats')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='cats')

    name = models.CharField(max_length=16)
    color = models.CharField(max_length=16)
    birth_year = models.IntegerField()
    image = models.ImageField(upload_to='cats/images/', null=True, blank=True)

    class Meta:
        unique_together = ['name', 'owner']

    def __str__(self):
        return self.name
