from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from hotel_app.models import User, MenuItem, OrderItem, Order, Receipt, SalesReport, Inventory
from django.utils.timezone import now
from django.db import models

# Helper function to validate positive numbers
def validate_positive(value):
    if value < 0:
        raise serializers.ValidationError("Value cannot be negative.")
    return value

# User Serializer 
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'date_joined']
        read_only_fields = ['date_joined', 'username', 'email']  # Prevent changes to username & email

    def create(self, validated_data):
        role = validated_data.get('role', 'customer')

        if self.context['request'].user.is_staff:  # Admin creating a user
            validated_data['password'] = make_password(validated_data['password'])
            return super().create(validated_data)
        elif role != 'customer':  # Customers cannot set roles
            raise serializers.ValidationError("Only admins can create staff accounts.")
        else:
            validated_data['role'] = 'customer'
            validated_data['password'] = make_password(validated_data['password'])
            return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user

        # Prevent customers from updating their role
        if not user.is_staff and 'role' in validated_data:
            raise serializers.ValidationError({"role": "Only admins can change user roles."})

        # If updating password, hash it
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])

        return super().update(instance, validated_data)


# MenuItem Serializer 
class MenuItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[validate_positive])
    quantity = serializers.IntegerField(validators=[validate_positive])

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'category', 'availability', 'quantity', 'product_photo']


# OrderItem Serializer 
class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menu_item', 'quantity', 'price_at_time_of_order']


# Order Serializer 
class OrderSerializer(serializers.ModelSerializer): 
    customer = serializers.SerializerMethodField()  # Return full name or username
    items = serializers.PrimaryKeyRelatedField(
        many=True, queryset=MenuItem.objects.all(), write_only=True
    ) 
    item_details = serializers.SerializerMethodField()  # Show full menu item details
 
    class Meta:
        model = Order
        fields = ["id", "customer", "items","item_details", "total_price", "status", "created_at"]
        read_only_fields = ["customer", "total_price", "status", "created_at"]  # Don't require them in input

    def create(self, validated_data):
        """Create an order and calculate total price based on selected menu item IDs."""
        menu_items = validated_data.pop("items", [])  # This is a list of MenuItem instances
        item_ids = [item.id for item in menu_items]  # Extract menu item IDs

        print("🚀 DEBUG: Received item_ids:", item_ids)  # Debugging output
        print("🚀 DEBUG: Raw items in validated_data:", validated_data.get("items"))

        if not isinstance(item_ids, list):
            raise serializers.ValidationError({"items": "Invalid data format. Expected a list of menu item IDs."})

        user = self.context["request"].user  # Get logged-in user
        order = Order.objects.create(customer=user)

        total_price = 0
        for item_id in item_ids:
            try:
                menu_item = MenuItem.objects.get(id=item_id)  # Fetch menu item from DB
                print("🚀 DEBUG: Processing menu_item:", menu_item.name)  # Debug output
            except MenuItem.DoesNotExist:
                raise serializers.ValidationError({"items": f"Menu item with ID {item_id} not found."})

            # Create OrderItem
            order_item = OrderItem.objects.create(order=order, menu_item=menu_item, quantity=1)
            total_price += order_item.get_total_price()
        
        # Update total price and save order
        order.total_price = total_price
        order.save()

        return order # return the order object

    def get_item_details(self, obj):
        return [
            {
                "id": item.menu_item.id,
                "name": item.menu_item.name,
                "price": str(item.menu_item.price)
            }
            for item in obj.orderitem_set.all()
        ]
    
    def get_customer(self, obj):
        full_name = f"{obj.customer.first_name} {obj.customer.last_name}".strip()
        return full_name if full_name else obj.customer.username


# Receipt Serializer 
# Order Summary Serializer
class OrderSummarySerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "items"]

    def get_items(self, obj):
        return [
            {
                "menu_item": item.menu_item.name,
                "quantity": item.quantity,
                "total_price": item.get_total_price(),
            }
            for item in obj.orderitem_set.all()
        ]

# Receipt Serializer
class ReceiptSerializer(serializers.ModelSerializer):
    orders = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Order.objects.exclude(receipts__isnull=False),  # Exclude orders linked to a receipt from selection
        write_only=True,
    )  # Allow selecting only unassigned orders
    order_details = serializers.SerializerMethodField()  # Show order details in response
    waiter = serializers.CharField(source="waiter.username", read_only=True)

    class Meta:
        model = Receipt
        fields = ["id", "orders", "order_details", "waiter", "total_amount", "printed", "settled", "printed_at"]
        read_only_fields = ["order_details", "total_amount", "printed_at"]  # Auto-generated fields

    def create(self, validated_data):
        # Create a receipt with selected orders and auto-calculate total amount.
        order_ids = validated_data.pop("orders", [])  # Get only IDs, not objects
        user = self.context["request"].user  # Get the logged-in user

        if not order_ids:
            raise serializers.ValidationError({"orders": "At least one order is required to create a receipt."})

        # Step 1: Create Receipt FIRST (without orders)
        receipt = Receipt.objects.create(waiter=user)  

        # Step 2: Add orders using IDs
        receipt.orders.set(order_ids)  # Ensure only order IDs are passed

        # Step 3: Recalculate total and update receipt
        receipt.total_amount = receipt.calculate_total_amount()
        receipt.save(update_fields=["total_amount"])

        return receipt

    def get_order_details(self, obj):
        # Return detailed info of orders in the receipt.
        return [
            {
                "order_id": order.id,
                "total_price": order.total_price,
                "items": [
                    {
                        "menu_item": item.menu_item.name,
                        "quantity": item.quantity,
                        "price": str(item.menu_item.price)
                    }
                    for item in order.orderitem_set.all()
                ],
            }
            for order in obj.orders.all()
        ]
    
# SalesReport Serializer 
class SalesReportSerializer(serializers.ModelSerializer):
    waiter = serializers.CharField(source="waiter.username", read_only=True)  # Display waiter’s username
    date = serializers.DateField(format="%Y-%m-%d", read_only=True)  # Ensure date is formatted properly
    printed_receipts_count = serializers.SerializerMethodField()
    settled_receipts_count = serializers.SerializerMethodField()
    total_printed_amount = serializers.SerializerMethodField()
    total_settled_amount = serializers.SerializerMethodField()

    class Meta:
        model = SalesReport
        fields = [
            "waiter",
            "date",
            "printed_receipts_count",
            "settled_receipts_count",
            "total_printed_amount",
            "total_settled_amount",
        ]

    def get_printed_receipts_count(self, obj):
        """Count receipts that have been printed today."""
        return Receipt.objects.filter(waiter=obj.waiter, printed=True, printed_at__date=now().date()).count()

    def get_settled_receipts_count(self, obj):
        """Count receipts that have been settled today."""
        return Receipt.objects.filter(waiter=obj.waiter, settled=True, printed_at__date=now().date()).count()

    def get_total_printed_amount(self, obj):
        """Sum the total amount of printed receipts today."""
        return Receipt.objects.filter(waiter=obj.waiter, printed=True, printed_at__date=now().date()).aggregate(
            total=models.Sum("total_amount")
        )["total"] or 0

    def get_total_settled_amount(self, obj):
        """Sum the total amount of settled receipts today."""
        return Receipt.objects.filter(waiter=obj.waiter, settled=True, printed_at__date=now().date()).aggregate(
            total=models.Sum("total_amount")
        )["total"] or 0



# Inventory Serializer 
class InventorySerializer(serializers.ModelSerializer):
    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = ['id', 'item_name', 'quantity', 'threshold', 'is_low_stock']
        read_only_fields = ['is_low_stock']  

    def get_is_low_stock(self, obj):
        return obj.quantity <= obj.threshold

