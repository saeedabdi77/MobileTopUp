from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
