from django.db import models
from django.contrib.auth.models import User

class Table(models.Model):
    STATUS = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('bill_requested', 'Bill Requested'),
        ('closed', 'Closed'),
    ]
    table_number = models.IntegerField(unique=True)
    capacity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS, default='available')

    def __str__(self):
        return f"Table {self.table_number}"


class MenuItem(models.Model):
    CATEGORY = [
        ('starter', 'Starter'),
        ('main', 'Main'),
        ('drink', 'Drink'),
        ('dessert', 'Dessert'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS = [
        ('placed', 'Placed'),
        ('kitchen', 'In Kitchen'),
        ('served', 'Served'),
        ('completed', 'Completed'),
    ]
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS, default='placed')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def order_total(self):
        return sum(item.total() for item in self.items.all())



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, null=True, blank=True)
    custom_name = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    quantity = models.IntegerField()

    def total(self):
        if self.menu_item:
            return self.menu_item.price * self.quantity
        else:
            return self.price * self.quantity

    def display_name(self):
        return self.menu_item.name if self.menu_item else self.custom_name



class Bill(models.Model):
    STATUS = [
        ('not_generated', 'Not Generated'),
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    tax_percent = models.IntegerField(default=5)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='not_generated')
