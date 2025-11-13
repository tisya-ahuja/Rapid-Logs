from celery import shared_task
from .models import User, Transaction
from .utils import format_report
from .mail import send_email
import datetime
import csv
import requests #plural
import json

@shared_task(ignore_results = False, name = "download_csv_report")
def csv_report():
    transactions = Transaction.query.all() # admin
    csv_file_name = f"transaction_{datetime.datetime.now().strftime("%f")}.csv" #transaction_123456.csv
    with open(f'static/{csv_file_name}', 'w', newline = "") as csvfile:
    # csvfile = open(f'static/{csv_file_name}', 'w', newline = "")
        sr_no = 1
        trans_csv = csv.writer(csvfile, delimiter = ',')
        trans_csv.writerow(['Sr No.', 'Transaction Name', 'Type', 'Created at', 'Delivery Date', 'Source', 'Destination', 'Internal Status', 'Delivery Status', 'Amount', 'Username'])
        for t in transactions:
            this_trans = [sr_no, t.name, t.type, t.date, t.delivery, t.source, t.destination, t.internal_status, t.delivery_status, t.amount, t.bearer.username]
            trans_csv.writerow(this_trans)
            sr_no += 1

    return csv_file_name

@shared_task(ignore_results = False, name = "monthly_report")
def monthly_report():
    users = User.query.all()
    for user in users[1:]:
        user_data = {}
        user_data['username'] = user.username
        user_data['email'] = user.email
        user_trans = []
        for transaction in user.trans:
            this_trans = {}
            this_trans["id"] = transaction.id
            this_trans["name"] = transaction.name
            this_trans["type"] = transaction.type
            this_trans["source"] = transaction.source
            this_trans["destination"] = transaction.destination
            this_trans["delivery"] = transaction.delivery
            this_trans["amount"] = transaction.amount
            this_trans["user"] = transaction.bearer.username #/current_user.id 
            user_trans.append(this_trans)
        user_data['transactions'] = user_trans
        message = format_report('templates/mail_details.html', user_data)
        send_email(user.email, subject = "Monthly transaction Report - Fast Logistics", message = message)
    return "Monthly reports sent"

@shared_task(ignore_results = False, name = "delivery_update")
def delivery_report(username):
    text = f"Hi {username}, your delivery status has been updated. Please check the app at http://127.0.0.1:5000"
    response = requests.post("https://chat.googleapis.com/v1/spaces/AAAAGfF3foI/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=gpn4rKlqCta9pKqgherO4fwknc0i4YMj06UkaRJW4CU", json = {"text": text})
    print(response.status_code)
    return "The delivery is sent to user"

    
    # https://chat.googleapis.com/v1/spaces/AAAAGfF3foI/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=gpn4rKlqCta9pKqgherO4fwknc0i4YMj06UkaRJW4CU




    # |||||||||||||||||||||||||||||||||||||||||| ---> 10 mins 
    # |\\\\\\\\\\\\\\\\\\\|\\\\\\\\\\\\\\\\\\\\\ ---> with cache  