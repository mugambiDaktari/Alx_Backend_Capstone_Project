from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from hotel_app.models import MenuItem, Order, Receipt, Inventory, SalesReport

# Create your tests here.
class HotelAppTestCase(TestCase):
    def setUp(self):
        """Set up test users, menu items, and initial objects."""
        self.client = APIClient()
        
        # Create an admin user
        self.admin = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        
        # Create a staff user
        self.staff = get_user_model().objects.create_user(
            username="staff", email="staff@example.com", password="staffpass", is_staff=True
        )

        # Create a customer user
        self.customer = get_user_model().objects.create_user(
            username="customer", email="customer@example.com", password="custpass"
        )

        # Create a menu item
        self.menu_item = MenuItem.objects.create(
            name="Burger", 
            price=5.00, 
            category="Food", 
            availability=True,
            quantity=100,  # Set initial quantity
            product_photo=None  # No image for this test case
        )
        
        # Create an order linked to the customer
        self.order = Order.objects.create(customer=self.customer)
        self.order.items.add(self.menu_item)

        # Create a receipt linked to the order
        # self.receipt = Receipt.objects.create(waiter=self.staff, total_amount=5.00, printed=True)

        # Create an inventory item
        self.inventory = Inventory.objects.create( item_name="Lettuce", quantity=100,  threshold=50)

        # Authenticate as admin for most tests
        self.client.force_authenticate(user=self.admin)


    def test_customer_can_create_order(self):
        # Ensure customers can place orders.
        self.client.force_authenticate(user=self.customer)
        data = {"items": [self.menu_item.id]}  # Order a single menu item whose id is the one provided
        response = self.client.post("/api/orders/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_user_cannot_create_order(self):
        # Ensure unauthenticated users can place orders.
        self.client.force_authenticate(user=None)
        data = {"items": [self.menu_item.id]}  # Order a single menu item whose id is the one provided
        response = self.client.post("/api/orders/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_admin_can_create_inventory(self):
        # Ensure only an admin can create an inventory item.
        data = {"item_name": "Tomatoes", "quantity": 50, "threshold": 50}
        response = self.client.post("/api/inventory/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_staff_cannot_create_inventory(self):
        # Ensure staff users cannot create inventory items.
        self.client.force_authenticate(user=self.staff)
        data = {"item_name": "Tomatoes", "quantity": 50, "threshold": 50}
        response = self.client.post("/api/inventory/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_create_inventory(self):
        # Ensure customer users cannot create inventory items.
        self.client.force_authenticate(user=self.customer)
        data = {"item_name": "Tomatoes", "quantity": 50, "threshold": 50}
        response = self.client.post("/api/inventory/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_inventory(self):
        # Ensure an admin can delete an inventory item.
        response = self.client.delete(f"/api/inventory/{self.inventory.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)  

    def test_staff_cannot_delete_inventory(self):
        # Ensure staff users cannot delete inventory items.
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(f"/api/inventory/{self.inventory.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_delete_inventory(self):
        # Ensure customers cannot delete inventory items.
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(f"/api/inventory/{self.inventory.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)