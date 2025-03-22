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