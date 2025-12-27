from django.urls import path
from .views import *

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('table/<int:table_id>/', table_detail),
    path('order/status/<int:order_id>/<str:status>/', update_order_status),
    path('bill/generate/<int:order_id>/', generate_bill),
    path('bill/<int:bill_id>/', bill_view),
    path('bill/pay/<int:bill_id>/', pay_bill),
    path('bill/download/<int:bill_id>/', download_bill),
    path('admin-login/', admin_login, name='admin_login'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),

]
