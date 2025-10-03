# E-commerce System - Version 1.0
# Basic implementation of shopping cart and order processing
# This line will be DELETED in version 2.0
# Another line that will be DELETED
# Yet another DELETED line for testing

import datetime
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)
# OLD logging level - will be DELETED
# debug_mode = True - DELETED LINE

class Product:
    def __init__(self, id, name, price, category):
        self.id = id
        self.name = name
        self.price = Decimal(str(price))
        self.category = category
        self.stock = 0
        # old_field = None - DELETED LINE

    def update_stock(self, quantity):
        self.stock += quantity
        logger.info(f"Updated stock for {self.name}: {self.stock}")

    def get_info(self):
        return f"{self.name} - ${self.price}"
        # old_method_logic - DELETED

class CartItem:
    def __init__(self, product, quantity=1):
        self.product = product
        self.quantity = quantity
        # deprecated_field - DELETED LINE

    def get_subtotal(self):
        return self.product.price * self.quantity

def calculate_total(items):
    total = Decimal('0')
    for item in items:
        total += item.get_subtotal()
    return total

def process_order(order):
    items = order.get_items()
    total = calculate_total(items)
    # OLD COMMENT: legacy tax calculation - DELETED

    if total > 100:
        discount = total * Decimal('0.1')
        total = total - discount

    return total

class ShoppingCart:
    def __init__(self):
        self.items = []
        self.created_at = datetime.datetime.now()
        # old_cart_id = None - DELETED LINE

    def add_item(self, product, quantity=1):
        cart_item = CartItem(product, quantity)
        self.items.append(cart_item)

    def remove_item(self, product):
        self.items = [item for item in self.items if item.product.id != product.id]

    def get_total(self):
        return calculate_total(self.items)

    def clear(self):
        self.items = []

class Order:
    def __init__(self, cart, customer):
        self.cart = cart
        self.customer = customer
        self.order_date = datetime.datetime.now()
        self.status = "pending"

    def get_items(self):
        return self.cart.items

    def confirm(self):
        self.status = "confirmed"
        logger.info(f"Order confirmed for {self.customer}")

class Customer:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.orders = []

    def place_order(self, cart):
        order = Order(cart, self)
        self.orders.append(order)
        return order

# Utility functions
def format_price(amount):
    return f"${amount:.2f}"

def validate_email(email):
    return "@" in email and "." in email

# ============================================
# SECTION 2: Additional Helper Functions
# These lines will be DELETED or MODIFIED
# ============================================

def calculate_shipping(weight, distance):
    # OLD shipping calculation - DELETED
    base_rate = 5.00
    return base_rate + (weight * 0.5)

def apply_tax(amount, tax_rate=0.07):
    # Simple tax calculation - will be REPLACED
    return amount * (1 + tax_rate)

# OLD function - will be DELETED
def legacy_discount(amount):
    if amount > 50:
        return amount * 0.95
    return amount

class PaymentProcessor:
    # OLD payment system - many lines will be DELETED
    def __init__(self):
        self.api_key = "old_api_key"
        self.endpoint = "https://old-payment-api.example.com"
        # deprecated_field = None - DELETED

    def process_payment(self, amount, card_number):
        # Old implementation - will be REPLACED
        return {"status": "success", "transaction_id": "12345"}

    def refund(self, transaction_id):
        # Old refund logic - DELETED
        return True

# ============================================
# SECTION 3: Inventory Management
# Mix of DELETIONS, INSERTIONS, and REPLACEMENTS
# ============================================

class Inventory:
    def __init__(self):
        self.items = {}
        # old_tracking_id = None - DELETED

    def add_product(self, product_id, quantity):
        if product_id in self.items:
            self.items[product_id] += quantity
        else:
            self.items[product_id] = quantity

    def remove_product(self, product_id, quantity):
        if product_id in self.items:
            self.items[product_id] -= quantity
            if self.items[product_id] <= 0:
                del self.items[product_id]

    def check_availability(self, product_id):
        return self.items.get(product_id, 0)

    # OLD method - will be DELETED
    def legacy_stock_report(self):
        for pid, qty in self.items.items():
            print(f"Product {pid}: {qty} units")

# ============================================
# SECTION 4: Discount and Promotion System
# Heavy modifications expected here
# ============================================

class DiscountCode:
    # OLD discount system - DELETED
    def __init__(self, code, amount):
        self.code = code
        self.amount = amount
        self.used = False

    def apply(self, total):
        # Simple percentage discount - REPLACED
        if not self.used:
            self.used = True
            return total * (1 - self.amount)
        return total

# OLD promotional class - DELETED
class SeasonalPromotion:
    def __init__(self, name, discount_rate):
        self.name = name
        self.discount_rate = discount_rate

    def is_active(self):
        # Check if promotion is currently active
        return True

# ============================================
# SECTION 5: Reporting and Analytics
# Some functions will be DELETED, others MODIFIED
# ============================================

def generate_sales_report(start_date, end_date):
    # OLD reporting logic - will be REPLACED
    print(f"Sales report from {start_date} to {end_date}")
    return {"total_sales": 1000, "total_orders": 50}

def calculate_revenue(orders):
    total = 0
    for order in orders:
        total += order.get_total()
    return total

# OLD analytics function - DELETED
def track_user_behavior(user_id, action):
    print(f"User {user_id} performed {action}")

def export_data(format="csv"):
    # OLD export logic - will be MODIFIED
    if format == "csv":
        return "data.csv"
    return "data.json"

# ============================================
# SECTION 6: User Authentication
# Will be completely REPLACED in v2
# ============================================

class User:
    # OLD user model - DELETED fields
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.is_active = True
        # old_session_id = None - DELETED

    def authenticate(self, password):
        # Simple password check - INSECURE, will be REPLACED
        return self.password == password

    def reset_password(self, new_password):
        self.password = new_password

# OLD session management - DELETED
def create_session(user):
    return {"user_id": user.username, "expires": "2024-12-31"}

# ============================================
# SECTION 7: Notification System
# Mix of changes
# ============================================

def send_email(to, subject, body):
    # OLD email sending - DELETED
    print(f"Sending email to {to}")
    print(f"Subject: {subject}")
    return True

def send_sms(phone, message):
    # OLD SMS service - will be REPLACED
    print(f"SMS to {phone}: {message}")
    return True

# OLD notification class - DELETED
class NotificationManager:
    def __init__(self):
        self.pending = []

    def queue_notification(self, recipient, message):
        self.pending.append({"to": recipient, "msg": message})

    def send_all(self):
        for notif in self.pending:
            print(f"Sending: {notif}")
        self.pending = []

# ============================================
# SECTION 8: Configuration and Settings
# Will have DELETIONS
# ============================================

# Global configuration - OLD values, will be DELETED
CONFIG = {
    "app_name": "E-commerce v1.0",
    "debug_mode": True,
    "max_cart_items": 100,
    "session_timeout": 3600,
    # old_api_endpoint - DELETED
}

def get_config(key):
    return CONFIG.get(key)

def set_config(key, value):
    CONFIG[key] = value

# OLD initialization - DELETED
def initialize_app():
    print("Initializing application v1.0")
    return True

# ============================================
# SECTION 9: Error Handling
# Some error classes will be DELETED
# ============================================

class PaymentError(Exception):
    pass

class InventoryError(Exception):
    pass

# OLD error class - DELETED
class LegacyError(Exception):
    pass

def handle_error(error):
    # OLD error handling - will be REPLACED
    print(f"Error occurred: {error}")
    return False

# ============================================
# SECTION 10: Main Application Logic
# Final section with various changes
# ============================================

def main():
    print("E-commerce System v1.0")
    # OLD initialization code - DELETED
    print("System ready")

if __name__ == "__main__":
    main()

# END OF FILE - Version 1.0
# Total lines: ~300
