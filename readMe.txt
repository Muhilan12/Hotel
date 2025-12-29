Restaurant Dine-In Management System

A Django-based mini system to manage restaurant dine-in tables, orders, billing, and staff roles with a live dashboard.


Features

1.Table Management
- 10 restaurant tables
- Table status:
  - Available
  - Occupied
  - Bill Requested
  - Closed
- Live dashboard with color-coded table view

2.Menu & Orders
- Menu items with:
  - Name
  - Category (Starter / Main / Drinks / Dessert)
  - Price
  - Availability
- Create orders per table
- Add multiple menu items
- Add custom food items (name, quantity, price)
- Order flow:
  - Placed → In Kitchen → Served → Completed
- Table auto-sets to **Occupied** when order is placed

3.Billing
- Generate bill after order is served
- Bill shows:
  - Item list
  - Quantity
  - Subtotal
  - Tax (flat %)
  - Grand total
- Download bill as PDF
- Mark bill as paid
- On payment:
  - Order completed
  - Table reset to Available

4.User Roles
- **Waiter**: Create orders, send to kitchen, mark served
- **Cashier**: Generate bill, mark paid
- **Manager**: Manage tables & menu, view dashboard



Tech Stack
- Backend: Django
- Frontend: HTML, CSS, JavaScript
- Database: SQLite
- PDF Generation: ReportLab
- Authentication: Django Auth

---




run command : python manage.py runserver

Admin Login : Username= admin
              Password= admin123


