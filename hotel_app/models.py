from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from django.db.models import Sum, F
from django.db.models.functions import TruncDate

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('waiter', 'Waiter'),
        ('kitchen', 'Kitchen Staff'),
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
        ('customer', 'Customer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    date_joined = models.DateTimeField(auto_now_add=True)

class MenuItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    availability = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField(default=0)  # Track stock availability
    product_photo = models.ImageField(upload_to="menu_photos/", null=True, blank=True)  # Store menu item image

    

    def __str__(self):
        return self.name
    
class OrderItem(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time_of_order = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.price_at_time_of_order:
            self.price_at_time_of_order = self.menu_item.price  # Save price when order is created
        super().save(*args, **kwargs)

    def get_total_price(self):
        return self.price_at_time_of_order * self.quantity  # Use saved price
    


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('served', 'Served'),
        ('completed', 'Completed'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    items = models.ManyToManyField(MenuItem, through="OrderItem")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    receipt = models.ForeignKey("Receipt", on_delete=models.SET_NULL, null=True, blank=True, related_name="order_receipts")

    def calculate_total_price(self):
        total = self.orderitem_set.aggregate(total=Sum(F("price_at_time_of_order") * F("quantity")))["total"] or 0.00
        return total

    def update_total_price(self):
        self.total_price = self.calculate_total_price()
        self.save(update_fields=['total_price'])  # Avoid recursion in save()

    def save(self, *args, **kwargs):
        if self.pk:  # Only update total_price if Order already exists
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

class Receipt(models.Model):
    waiter = models.ForeignKey(User, on_delete=models.CASCADE)
    orders = models.ManyToManyField(Order, related_name="receipts")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    printed = models.BooleanField(default=False)
    settled = models.BooleanField(default=False)
    printed_at = models.DateTimeField(null=True, blank=True)

    def calculate_total_amount(self):
        """Calculate the total amount based on orders."""
        if self.pk:  # Ensure the Receipt is already saved
            return sum(order.total_price for order in self.orders.all())
        return 0  # Return 0 if the receipt is not saved yet

    def save(self, *args, **kwargs):
        """Save the receipt and update the total amount after adding orders."""
        super().save(*args, **kwargs)  # Save first to get an ID
        self.total_amount = self.calculate_total_amount()  # Now update the amount
        super().save(update_fields=["total_amount"])  # Save again to update amount



class SalesReport(models.Model):
    waiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales_reports")
    date = models.DateField(auto_now_add=True)  # Sales report per day
    printed_receipts_count = models.PositiveIntegerField(default=0)
    settled_receipts_count = models.PositiveIntegerField(default=0)
    total_printed_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_settled_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Sales Report - {self.waiter.username} - {self.date}"

@classmethod
def update_report(cls, waiter):
    """Update sales report for a waiter based on today's receipts."""
    today = now().date()  # Fix date issue
    receipts = Receipt.objects.filter(waiter=waiter, printed_at__date=today)

    # Count printed and settled receipts
    printed_count = receipts.count()
    settled_count = receipts.filter(settled=True).count()

    # Sum total amounts
    total_printed = receipts.aggregate(Sum("total_amount"))["total_amount__sum"] or 0.00
    total_settled = receipts.filter(settled=True).aggregate(Sum("total_amount"))["total_amount__sum"] or 0.00

    # Update or create sales report
    report, created = cls.objects.update_or_create(
        waiter=waiter,
        date=today,  # Use fixed date
        defaults={
            "printed_receipts_count": printed_count,
            "settled_receipts_count": settled_count,
            "total_printed_amount": total_printed,
            "total_settled_amount": total_settled,
        },
    )
    return report

# Inventory Model
class Inventory(models.Model):
    item = models.CharField(max_length=100, unique=True)
    quantity = models.PositiveIntegerField()
    threshold = models.PositiveIntegerField()

    def is_low_stock(self):
        return self.quantity <= self.threshold