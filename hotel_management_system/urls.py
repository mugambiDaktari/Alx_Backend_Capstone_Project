from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from hotel_app.views import (
    UserViewSet, MenuItemViewSet, OrderViewSet, OrderItemViewSet,
    ReceiptViewSet, SalesReportViewSet, InventoryViewSet,
    HomeView, RegisterView, UserLoginView, UserLogoutView
)

# DRF Router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user') 
router.register(r'menu-items', MenuItemViewSet, basename='menuitem')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='orderitem')
router.register(r'receipts', ReceiptViewSet, basename='receipt')
router.register(r'sales-reports', SalesReportViewSet, basename='salesreport')
router.register(r'inventory', InventoryViewSet, basename='inventory')



urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication & Home
    path('', HomeView.as_view(), name='homepage'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    # DRF API Endpoints
    path('api/', include(router.urls)),
]

