# Alx_Backend_Capstone_Project
This is an API-powered hotel order management system built with Django Rest Framework (DRF). This system allows users to manage menu items, orders, receipts, sales reports, and inventory while enforcing role-based access control.

Features
User Authentication & Role Management (Customers vs. Staff)
Menu Management (CRUD for food items)
Order Management (Customers place orders, staff processes them)
Receipts & Payments (Track printed and settled receipts)
Sales Reports (Daily reports on revenue and orders)
Inventory Tracking (Monitor stock levels and flag low stock)

Tech Stack
Backend: Django, Django Rest Framework (DRF)
Database: SQLite
Frontend (Planned): HTML/CSS with Django Templates

Setup & Installation
1. Clone the Repository 
git clone https://github.com/yourusername/hotel-management.git
cd hotel-management

2. Create a Virtual Environment & Install Dependencies
python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate     # For Windows

pip install -r requirements.txt

3. Run Migrations
python manage.py migrate

4. Create a Superuser
python manage.py createsuperuser

5. Start the Server
python manage.py runserver


API Endpoints

User Authentication
Method	  Endpoint	        Description	           Access
POST	  /api/users/	    Register a new user	   Open
GET	      /api/users/	    List all users	       Admin Only
GET	      /api/users/{id}/	Get user details	   Authenticated
PATCH	  /api/users/{id}/	Update user profile	   Authenticated
DELETE	  /api/users/{id}/	Delete a user	       Admin Only

Menu Management
Method	  Endpoint	              Description	              Access
GET	      /api/menu-items/	      List all menu items	      Open
POST	  /api/menu-items/	      Add a new menu item	      Staff Only
GET	      /api/menu-items/{id}/	  View menu item details	  Open
PUT	      /api/menu-items/{id}/   Update a menu item	      Staff Only
DELETE	  /api/menu-items/{id}/	  Remove a menu item	      Staff Only

Order Management
Method	  Endpoint	          Description	        Access
GET	      /api/orders/	      View all orders	    Staff Only
POST	  /api/orders/	      Place an order	    Customers
GET	      /api/orders/{id}/	  View order details	Authenticated
PATCH	  /api/orders/{id}/	  Update order status	Staff Only

Receipts & Payments
Method	Endpoint	         Description	                  Access
GET	    /api/receipts/	     View receipts	                  Staff Only
PATCH	/api/receipts/{id}/	 Update printed/settled status	  Staff Only

Sales Reports
Method	 Endpoint	            Description	                 Access
GET	     /api/sales-reports/	View today's sales report	 Staff Only

Inventory Management
Method	Endpoint	            Description	        Access
GET	    /api/inventory/	        View stock levels	Open
PATCH	/api/inventory/{id}/	Update stock	    Staff Only


Access endpoints are defined as follows: and how to use them.
Get access and refresh token 
POST
http://127.0.0.1:8000/api/token/
{
  "username": "admin",
  "password": "password123"
}
Get a new access token using the refresh token.
POST
http://127.0.0.1:8000/api/token/refresh/
{
  "refresh": "refresh_token"
}
Checks if a token is valid.
POST
http://127.0.0.1:8000/api/token/verify/
{
  "token": "access_token"
}
List all users (Admins only)
GET
 http://127.0.0.1:8000/api/users/
Retrieve a user
GET
http://127.0.0.1:8000/api/users/{id}/
Create a user (Admin creates staff accounts manually)
POST 
http://127.0.0.1:8000/api/users/
Update a user (Admin only)
PUT 
http://127.0.0.1:8000/api/users/{id}/
Delete a user (Admin only)
DELETE 
http://127.0.0.1:8000/api/users/{id}/


Menu Management
List all menu items
GET 
http://127.0.0.1:8000/api/menu-items/
Retrieve a specific menu item
GET 
http://127.0.0.1:8000/api/menu-items/{id}/
Create a menu item (Staff/Admin only)


POST 
http://127.0.0.1:8000/api/menu-items/
{
  "name": "Pizza",
  "price": 800.00,
  "available": true,
  "category": "",
  "quantity": 10
}
Update a menu item (Staff/Admin only)
PUT 
http://127.0.0.1:8000/api/menu-items/{id}/
{
    "id": 8,
    "name": "Pizza",
    "price": "800.00",
    "category": "SNACKS",
    "availability": true,
    "quantity": 10,
}
Delete a menu item (Staff/Admin only)
DELETE 
http://127.0.0.1:8000/api/menu-items/{id}/

Order Management
Customers place an order
POST
http://127.0.0.1:8000/api/orders/
{
  "items": [{id}]
}
List all orders (Admins & Staff only)
GET
 http://127.0.0.1:8000/api/orders/
Retrieve a specific order
GET 
http://127.0.0.1:8000/api/orders/{id}/
Update order status (Staff/Admin only)
PUT 
http://127.0.0.1:8000/api/orders/{id}/
{
  "items": [{id} ,{id}, {id}, …]
}
Delete an Order (Admin Only)
DELETE 
http://127.0.0.1:8000/api/orders/{id}/
Authorization: Bearer <admin-token>

Receipt Generation & Payment Handling
List all receipts (Admins & Staff only)
GET 
http://127.0.0.1:8000/api/receipts/
Retrieve a specific receipt
GET 
http://127.0.0.1:8000/api/receipts/{id}/
Update receipt status (Mark as printed or settled)
PUT 
http://127.0.0.1:8000/api/receipts/{id}/   Adds items on a receipt instead of changing receipt status
{
  "orders": [1, 7, 12]
}
Delete a Receipt (Admin Only)
DELETE 
http://127.0.0.1:8000/api/receipts/{id}/
Authorization: Bearer <admin-token>

Sales Reports
Get today's sales report (Admins & Managers only)
GET 
http://127.0.0.1:8000/api/sales-reports/
Tracks printed & settled receipts per waiter.

Shows total amount collected.

Inventory Management
Create an Inventory Item (Admin Only)
POST 
http://127.0.0.1:8000/api/inventory/
Authorization: Bearer <admin-token>
{
    "name": "Tomatoes",
    "quantity": 50,
    "unit": "kg"
}
List all inventory items (Admins & Staff only)
GET 
http://127.0.0.1:8000/api/inventory/
Retrieve a specific inventory item
GET 
http://127.0.0.1:8000/api/inventory/{id}/
Update stock levels (Staff/Admin only)
PUT 
http://127.0.0.1:8000/api/inventory/{id}/
Delete an Inventory Item (Admin Only)
DELETE 
http://127.0.0.1:8000/api/inventory/{id}/
Authorization: Bearer <admin-token>

Tesh tokens
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0NDEwODY5OSwiaWF0IjoxNzQzNTAzODk5LCJqdGkiOiI1YWVlYzhiODRlOGM0YWRhYjYzODMyNzQyNGRhZTUxYiIsInVzZXJfaWQiOjh9.UXjrTG6D2lKygsbAh0ln0iuKeYSMTAE_g6lK79qR6ZU",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQzNTkwMjk5LCJpYXQiOjE3NDM1MDM4OTksImp0aSI6IjRiY2U5YzU0ODhjZTQ4Y2JiNDI3NjMyMDkwZjlmZDc5IiwidXNlcl9pZCI6OH0.dK_5rB4p6Uddx08eiHsmHCqBGda9Tzf3DYeZdoLJlJ4"
}
 
