# Generated by Django 5.1.7 on 2025-04-01 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_app', '0002_alter_receipt_orders_alter_receipt_waiter'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventory',
            old_name='item',
            new_name='item_name',
        ),
    ]
