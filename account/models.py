from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Seller(AbstractUser):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
