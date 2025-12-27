from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import HttpResponse
from reportlab.pdfgen import canvas

@login_required
def dashboard(request):
    tables = Table.objects.all().order_by('table_number')
    latest_order = Order.objects.last()
    return render(request, 'dining/dashboard.html', {
        'tables': tables,
        'latest_order': latest_order
    })


@login_required
def table_detail(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    menu = MenuItem.objects.filter(is_available=True)
    order = Order.objects.filter(table=table).last()

    if request.method == 'POST':
        # If table is available, create new order
        if table.status == 'available' or not order or order.status == 'completed':
            order = Order.objects.create(table=table, created_by=request.user)

        # Add existing menu items from the form
        for item in menu:
            qty = int(request.POST.get(f"menu_{item.id}", 0))
            if qty > 0:
                OrderItem.objects.create(order=order, menu_item=item, quantity=qty)

        # Add custom menu items
        custom_names = request.POST.getlist('custom_name')
        custom_qtys = request.POST.getlist('custom_qty')
        custom_prices = request.POST.getlist('custom_price')

        for name, qty, price in zip(custom_names, custom_qtys, custom_prices):
            if name.strip() != '' and int(qty) > 0:
                OrderItem.objects.create(
                    order=order,
                    menu_item=None,           # Not linked to main menu
                    custom_name=name,
                    quantity=int(qty),
                    price=float(price)
                )

        table.status = 'occupied'
        table.save()
        request.session['alert'] = "🍳 New Order Placed!"
        return redirect(f'/table/{table.id}/')

    return render(request, 'dining/table_detail.html', {
        'table': table,
        'menu': menu,
        'order': order
    })



@login_required
def update_order_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)

    if status not in ['kitchen', 'served', 'completed']:
        return HttpResponse("Invalid status")

    order.status = status
    order.save()

    return redirect(f'/table/{order.table.id}/')



@login_required
def generate_bill(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status != 'served':
        return HttpResponse("Order not served yet")

    subtotal = sum(i.total() for i in order.items.all())
    tax_percent = 5
    tax_amount = subtotal * tax_percent / 100
    grand_total = subtotal + tax_amount

    bill, created = Bill.objects.get_or_create(
        order=order,
        defaults={
            'tax_percent': tax_percent,
            'total_amount': grand_total,
            'status': 'pending'
        }
    )

    order.table.status = 'bill_requested'
    order.table.save()

    return redirect(f'/bill/{bill.id}/')



@login_required
def bill_view(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    return render(request, 'dining/bill.html', {'bill': bill})


@login_required
def pay_bill(request, bill_id):
    # Get the bill
    bill = get_object_or_404(Bill, id=bill_id)

    # 1️⃣ Mark the bill as paid
    bill.status = 'paid'
    bill.save()

    # 2️⃣ Get the table and reset status
    table = bill.order.table
    table.status = 'available'
    table.save()

    # 3️⃣ Mark the current order as completed
    current_order = bill.order
    current_order.status = 'completed'
    current_order.save()

    # 4️⃣ Close any other old orders for this table (just in case)
    Order.objects.filter(table=table).exclude(id=current_order.id).update(status='completed')

    # 5️⃣ Redirect to dashboard
    return redirect('/admin-dashboard/')



from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from datetime import datetime

@login_required
def download_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bill_table_{bill.order.table.table_number}.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Restaurant Header
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - 2*cm, "🍽️  Restaurant")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height - 2.7*cm, "123 Food Street, City, Country")
    c.drawCentredString(width/2, height - 3.2*cm, "Phone: +91 1234567890")

    # Bill Info
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, height - 4*cm, f"Table: {bill.order.table.table_number}")
    c.drawString(10*cm, height - 4*cm, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}")

    # Table header
    c.setFont("Helvetica-Bold", 12)
    y = height - 5*cm
    c.drawString(2*cm, y, "Item")
    c.drawString(9*cm, y, "Qty")
    c.drawString(12*cm, y, "Price")
    c.drawString(15*cm, y, "Total")
    y -= 0.3*cm
    c.line(2*cm, y, 19*cm, y)
    y -= 0.3*cm

    # Items
    c.setFont("Helvetica", 12)
    for item in bill.order.items.all():
        name = item.menu_item.name if item.menu_item else item.custom_name
        unit_price = item.menu_item.price if item.menu_item else item.price
        total_price = item.total()
        c.drawString(2*cm, y, name)
        c.drawString(9*cm, y, str(item.quantity))
        c.drawString(12*cm, y, f"₹{unit_price}")
        c.drawString(15*cm, y, f"₹{total_price}")
        y -= 0.6*cm

    # Totals
    y -= 0.3*cm
    c.line(2*cm, y, 19*cm, y)
    y -= 0.5*cm
    c.setFont("Helvetica-Bold", 12)
    subtotal = sum([i.total() for i in bill.order.items.all()])
    tax_amount = subtotal * bill.tax_percent / 100
    grand_total = subtotal + tax_amount
    c.drawRightString(17.5*cm, y, f"Subtotal: ₹{subtotal:.2f}")
    y -= 0.5*cm
    c.drawRightString(17.5*cm, y, f"Tax ({bill.tax_percent}%): ₹{tax_amount:.2f}")
    y -= 0.5*cm
    c.drawRightString(17.5*cm, y, f"Grand Total: ₹{grand_total:.2f}")

    # Footer
    y -= 1.5*cm
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(width/2, y, "Thank you for dining with us! 🍴")
    c.drawCentredString(width/2, y-0.5*cm, "Visit Again!")

    c.showPage()
    c.save()

    return response



from datetime import date
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncHour
from django.shortcuts import render

from .models import Order


@login_required
def admin_dashboard(request):
    today = date.today()

    # ---- ORDER COUNTS ----
    pending_orders = Order.objects.filter(
        status__in=['placed', 'kitchen']
    ).count()

    completed_orders = Order.objects.filter(
        status='completed'
    ).count()

    today_orders = Order.objects.filter(
        created_at__date=today
    ).count()

    # ---- HOURLY GRAPH DATA (SQLite Safe) ----
    hourly_qs = (
        Order.objects
        .filter(created_at__date=today)
        .annotate(hour=TruncHour('created_at'))
        .values('hour')
        .annotate(count=Count('id'))
        .order_by('hour')
    )

    hours = [h['hour'].strftime('%H:%M') for h in hourly_qs if h['hour']]
    counts = [h['count'] for h in hourly_qs]

    # ---- RECENT ORDERS ----
    recent_orders = (
        Order.objects
        .select_related('table')
        .prefetch_related('items__menu_item')
        .order_by('-created_at')[:10]
    )

    return render(request, 'dining/admin_dashboard.html', {
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'today_orders': today_orders,
        'hours': hours,
        'counts': counts,
        'recent_orders': recent_orders
    })



from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def admin_login(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('/admin-dashboard/')
        else:
            error = "Invalid admin credentials"

    return render(request, 'dining/admin_login.html', {'error': error})
