from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(FarmerProfile)
admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(FAQ)