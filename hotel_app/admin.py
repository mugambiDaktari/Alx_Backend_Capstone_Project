from django.contrib import admin
from .models import User, MenuItem, Order, OrderItem, Receipt, SalesReport, Inventory

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_staff', 'password', 'email', 'role',)
    search_fields = ('username', 'email')
admin.site.register(User, UserAdmin)
admin.site.register(MenuItem)   
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Receipt)
admin.site.register(SalesReport)
admin.site.register(Inventory)

