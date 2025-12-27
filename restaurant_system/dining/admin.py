from django.contrib import admin
from .models import *

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'table', 'status', 'created_at')

admin.site.register(Table)
admin.site.register(MenuItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Bill)
