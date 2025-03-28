from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order, OrderItem, Receipt, SalesReport
from django.utils.timezone import now
from decimal import Decimal


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



@receiver(post_save, sender=Receipt)
def update_sales_report(sender, instance, created, **kwargs):
    """Automatically update SalesReport when a receipt is printed or settled."""
    
    if not instance.printed and not instance.settled:
        return  # Ignore receipts that are neither printed nor settled

    sales_report, _ = SalesReport.objects.get_or_create(
        date=now().date(),
        waiter=instance.waiter
    )

    # If a new receipt is created and printed
    if created and instance.printed:
        sales_report.printed_receipts_count += 1
        sales_report.total_printed_amount += Decimal(instance.total_amount)

    # If a new receipt is created and settled
    if created and instance.settled:
        sales_report.settled_receipts_count += 1
        sales_report.total_settled_amount += Decimal(instance.total_amount)

    # If an existing receipt's status changed from NOT printed → printed
    elif not created:
        previous_instance = Receipt.objects.get(pk=instance.pk)
        
        if not previous_instance.printed and instance.printed:
            sales_report.printed_receipts_count += 1
            sales_report.total_printed_amount += Decimal(instance.total_amount)

        if not previous_instance.settled and instance.settled:
            sales_report.settled_receipts_count += 1
            sales_report.total_settled_amount += Decimal(instance.total_amount)

    sales_report.save()
