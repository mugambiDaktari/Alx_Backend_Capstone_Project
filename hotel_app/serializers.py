from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from hotel_app.models import User, MenuItem, OrderItem, Order, Receipt, SalesReport, Inventory

# Helper function to validate positive numbers
def validate_positive(value):
    if value < 0:
        raise serializers.ValidationError("Value cannot be negative.")
    return value

# ===================== User Serializer =====================
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


# ===================== MenuItem Serializer =====================
class MenuItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[validate_positive])
    quantity = serializers.IntegerField(validators=[validate_positive])

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'category', 'availability', 'quantity', 'product_photo']


# ===================== OrderItem Serializer =====================
class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menu_item', 'quantity', 'price_at_time_of_order']


# ===================== Order Serializer =====================
class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()  # Return full name or username
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'items', 'total_price', 'status', 'created_at', 'updated_at', 'receipt']

    def get_customer(self, obj):
        full_name = f"{obj.customer.first_name} {obj.customer.last_name}".strip()
        return full_name if full_name else obj.customer.username


# ===================== Receipt Serializer =====================
class ReceiptSerializer(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField()  # Custom field for order details
    waiter = serializers.CharField(source='waiter.username', read_only=True)  # Return only the waiter's username

    class Meta:
        model = Receipt
        fields = ['id', 'orders', 'waiter', 'total_amount', 'printed', 'settled', 'printed_at']

    def update(self, instance, validated_data):
        user = self.context['request'].user

        # Prevent customers from changing printed/settled status
        if not user.is_staff:
            validated_data.pop('printed', None)
            validated_data.pop('settled', None)

        return super().update(instance, validated_data)

    def get_orders(self, obj):
        # Return a list of menu items with quantity and total price per item
        orders_data = []
        for order in obj.orders.all():
            order_items = order.orderitem_set.all()  # Get all items in the order
            items_list = [
                {
                    "menu_item": item.menu_item.name,  # Name of the menu item
                    "quantity": item.quantity,
                    "total_price": item.get_total_price(),  # Price * Quantity
                }
                for item in order_items
            ]
            orders_data.append({
                "order_id": order.id,
                "items": items_list
            })
        return orders_data


# ===================== SalesReport Serializer =====================
class SalesReportSerializer(serializers.ModelSerializer):
    waiter = serializers.CharField(source='waiter.username', read_only=True)  # Return waiter's username
    date = serializers.DateField(format="%Y-%m-%d")  # Ensure date is formatted properly

    class Meta:
        model = SalesReport
        fields = [
            'id',
            'waiter',
            'date',
            'printed_receipts_count',
            'settled_receipts_count',
            'total_printed_amount',
            'total_settled_amount'
        ]


# ===================== Inventory Serializer =====================
class InventorySerializer(serializers.ModelSerializer):
    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = ['id', 'item', 'quantity', 'threshold', 'is_low_stock']
        read_only_fields = ['item']  # Prevents accidental renaming

    def get_is_low_stock(self, obj):
        return obj.quantity <= obj.threshold

