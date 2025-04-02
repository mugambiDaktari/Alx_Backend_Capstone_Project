from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.timezone import now

from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action

from hotel_app.models import User, MenuItem, Order, OrderItem, Receipt, SalesReport, Inventory
from hotel_app.serializers import (
    UserSerializer, MenuItemSerializer, OrderSerializer, OrderItemSerializer,
    ReceiptSerializer, SalesReportSerializer, InventorySerializer
)
from hotel_app.forms import UserRegistrationForm
from rest_framework import serializers
from django.db.models.signals import post_save
from django.dispatch import receiver



from django.db.models import Sum
from decimal import Decimal

# AUTHENTICATION VIEWS
class HomeView(TemplateView):
    template_name = "hotel_app/homepage.html"

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "hotel_app/register.html"
    success_url = reverse_lazy("homepage")  # Redirect after successful registration

class UserLoginView(LoginView):
    template_name = "hotel_app/login.html"

class UserLogoutView(LogoutView):
    next_page = "login"  # Redirect to login page after logout

# USER VIEWSET
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':  # Allow user registration
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]  # Only authenticated users can update/view

# MENU ITEM VIEWSET
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Anyone can view, only staff can modify
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'category', 'availability']  # Allows search by ?search=pizza

# ORDER VIEWSET
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().prefetch_related('items')  # Admins see all orders
        return Order.objects.filter(customer=user).prefetch_related('items')  # Customers see only their own
    def destroy(self, request, *args, **kwargs):
        # Ensure only admins (superusers) can delete orders.
        if not request.user.is_superuser:
            return Response({"error": "Only admins can delete orders. Please contact mugambiDaktari @https://www.linkedin.com/in/dr-mugambi-wycliff-77319511b/"}, status=403)
        return super().destroy(request, *args, **kwargs)
    

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if request.user != order.customer and not request.user.is_staff:
            return Response({"detail": "You can only update your own orders."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        if request.user != order.customer and not request.user.is_staff:
            return Response({"detail": "You can only cancel your own orders."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """ Allow users to add items to an existing order. """
        order = self.get_object()
        if order.status != "pending":
            return Response({"error": "Cannot modify a non-pending order."}, status=status.HTTP_400_BAD_REQUEST)

        menu_item_id = request.data.get("menu_item_id")
        quantity = request.data.get("quantity", 1)

        try:
            menu_item = MenuItem.objects.get(id=menu_item_id)
        except MenuItem.DoesNotExist:
            return Response({"error": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND)

        order_item, created = OrderItem.objects.get_or_create(order=order, menu_item=menu_item)
        if not created:
            order_item.quantity += int(quantity)
            order_item.save()

        order.total_price = order.calculate_total_price()
        order.save()

        return Response({"message": "Item added successfully!"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        """ Allow users to remove items from an order, ensuring at least one item remains. """
        order = self.get_object()
        if order.status != "pending":
            return Response({"error": "Cannot modify a non-pending order."}, status=status.HTTP_400_BAD_REQUEST)

        menu_item_id = request.data.get("menu_item_id")

        try:
            order_item = OrderItem.objects.get(order=order, menu_item_id=menu_item_id)
        except OrderItem.DoesNotExist:
            return Response({"error": "Item not found in the order."}, status=status.HTTP_404_NOT_FOUND)

        if order.orderitem_set.count() == 1:
            return Response({"error": "An order must have at least one item."}, status=status.HTTP_400_BAD_REQUEST)

        order_item.delete()
        order.total_price = order.calculate_total_price()
        order.save()

        return Response({"message": "Item removed successfully!"}, status=status.HTTP_200_OK)

# ORDER ITEM VIEWSET
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

# RECEIPT VIEWSET
class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        receipt = self.get_object()
        
        # Customers should not be able to update 'printed' or 'settled'
        if not request.user.is_staff:
            if 'printed' in request.data or 'settled' in request.data:
                return Response({"detail": "Only staff can change receipt status."}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)
    def destroy(self, request, *args, **kwargs):
        # Ensure only admins (superusers) can delete receipts.
        if not request.user.is_superuser:
            return Response({"error": "Only admins can delete receipts. Please contact mugambiDaktari @https://www.linkedin.com/in/dr-mugambi-wycliff-77319511b/"}, status=403)
        return super().destroy(request, *args, **kwargs)
# SALES REPORT VIEWSET
class IsAdminOrManager(permissions.BasePermission):
    """
    Custom permission: Only allow admins and managers to view reports.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.role == "manager")

class SalesReportViewSet(viewsets.ReadOnlyModelViewSet):  # ReadOnly prevents creation
    serializer_class = SalesReportSerializer
    permission_classes = [IsAdminOrManager]

    def get_queryset(self):
        """
        Returns sales reports for today's date only, grouped by waiter.
        """
        today = now().date()

        # Get all distinct waiters who have printed/settled receipts today
        waiters = User.objects.filter(
            receipt__printed_at__date=today,
            receipt__printed=True
        ).distinct()

        # Create sales reports dynamically
        return [
            SalesReport(
                waiter=waiter,
                date=today
            )
            for waiter in waiters
        ]


@receiver(post_save, sender=Receipt)
def update_sales_report(sender, instance, **kwargs):
    """Automatically update sales report when receipt status changes"""
    today = now().date()
    sales_report, created = SalesReport.objects.get_or_create(waiter=instance.waiter, date=today)

    if instance.settled:  # Receipt is now settled
        sales_report.settled_receipts_count += 1
        # sales_report.total_settled_amount += instance.total_amount
        sales_report.total_settled_amount += Decimal(instance.total_amount)
        
        # If it was previously printed, adjust counts
        if instance.printed:
            sales_report.printed_receipts_count = max(0, sales_report.printed_receipts_count - 1)
            sales_report.total_printed_amount = Decimal(max(0, sales_report.total_printed_amount - instance.total_amount))

    elif instance.printed:  # Receipt is only printed (not settled)
        sales_report.printed_receipts_count += 1
        # sales_report.total_printed_amount += instance.total_amount
        sales_report.total_printed_amount += Decimal(instance.total_amount)
        # sales_report.total_printed_amount += Decimal(str(instance.total_amount))


    sales_report.save()

# INVENTORY VIEWSET
class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Ensure only admins (superusers) can create inventory items.
        if not request.user.is_superuser:
            return Response({"error": "Only admins can create inventory items. Please contact mugambiDaktari @https://www.linkedin.com/in/dr-mugambi-wycliff-77319511b/"}, status=403)
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Ensure only admins (superusers) can delete inventory items.
        if not request.user.is_superuser:
            return Response({"error": "Only admins can delete inventory items. Please contact mugambiDaktari @https://www.linkedin.com/in/dr-mugambi-wycliff-77319511b/"}, status=403)
        return super().destroy(request, *args, **kwargs)
