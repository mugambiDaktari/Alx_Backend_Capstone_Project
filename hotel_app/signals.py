from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order, OrderItem

@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    """Automatically update total_price in Order when an OrderItem is added, updated, or deleted."""
    order = instance.order
    order.total_price = order.calculate_total_price()
    order.save()

@receiver(post_save, sender=OrderItem)
def reduce_stock(sender, instance, created, **kwargs):
    """Reduce stock of a MenuItem when a new OrderItem is created."""
    if created:  # Only reduce stock if the OrderItem is newly created
        menu_item = instance.menu_item
        menu_item.quantity = max(0, menu_item.quantity - instance.quantity)  # Prevent negative stock
        menu_item.save()

