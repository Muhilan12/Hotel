
## Setup Instructions

1. Clone & Setup

git clone <repository-url>
cd restaurant_system
python -m venv venv
venv\Scripts\activate
pip install django reportlab


2. DB integration

python manage.py makemigrations
python manage.py migrate


3.UsperUser

python manage.py createsuperuser


4. user and Password

Username: admin
Password: admin123


5.Create Tables
open CMD 
python manage.py shell


from dining.models import Table
for i in range(1, 11):
    Table.objects.create(table_number=i, capacity=4)
exit() 


6.Run Server

python manage.py runserver













