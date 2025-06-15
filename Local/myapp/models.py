from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    is_farmer = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)


class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    farmer_name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='farmers/', blank=True)

    def __str__(self):
        return self.farm_name
