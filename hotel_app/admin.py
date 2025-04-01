from django.contrib import admin
from .models import User, MenuItem, Order, OrderItem, Receipt, SalesReport, Inventory

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_staff', 'password', 'email', 'role',)
    search_fields = ('username', 'email')
admin.site.register(User, UserAdmin)

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'availability', 'quantity')
    search_fields = ('name', 'category')
    list_filter = ('category', 'availability')
admin.site.register(MenuItem, MenuItemAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer',  'status',  'total_price', 'created_at',)
    search_fields = ('customer__username', 'status')
    list_filter = ('status',)
admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'price_at_time_of_order')
    search_fields = ('order__customer__username', 'menu_item__name')
    list_filter = ('menu_item__category', 'menu_item__availability')
admin.site.register(OrderItem, OrderItemAdmin)


admin.site.register(Receipt)
admin.site.register(SalesReport)
admin.site.register(Inventory)

