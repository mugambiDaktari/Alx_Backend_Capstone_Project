from django.contrib import admin
from .models import User, MenuItem, Order, OrderItem, Receipt, SalesReport, Inventory

# Register your models here.
admin.site.register(User)
admin.site.register(MenuItem)   
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Receipt)
admin.site.register(SalesReport)
admin.site.register(Inventory)

