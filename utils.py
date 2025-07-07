import os
import requests
from datetime import datetime, timedelta
from models import Invoice, CashRegisterEntry, CashClosing, Customer
from app import db
from sqlalchemy import func

def generate_invoice_number():
    """Generate a unique invoice number with format CW-0000"""
    # Get the last invoice number
    last_invoice = Invoice.query.filter(
        Invoice.invoice_number.like("CW-%")
    ).order_by(Invoice.id.desc()).first()
    
    if last_invoice:
        # Extract the sequence number and increment
        last_seq = int(last_invoice.invoice_number.split('-')[-1])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    
    return f"CW-{new_seq:04d}"

def format_lempiras(amount):
    """Format amount in Lempiras currency"""
    return f"L {amount:,.2f}"

def calculate_cash_total(cash_data):
    """Calculate total cash from denomination counts"""
    total = 0.0
    
    # Bills
    total += cash_data.get('bills_1000', 0) * 1000
    total += cash_data.get('bills_500', 0) * 500
    total += cash_data.get('bills_200', 0) * 200
    total += cash_data.get('bills_100', 0) * 100
    total += cash_data.get('bills_50', 0) * 50
    total += cash_data.get('bills_20', 0) * 20
    total += cash_data.get('bills_10', 0) * 10
    total += cash_data.get('bills_5', 0) * 5
    total += cash_data.get('bills_2', 0) * 2
    total += cash_data.get('bills_1', 0) * 1
    
    # Coins
    total += cash_data.get('coins_50c', 0) * 0.50
    total += cash_data.get('coins_20c', 0) * 0.20
    total += cash_data.get('coins_10c', 0) * 0.10
    total += cash_data.get('coins_5c', 0) * 0.05
    
    return round(total, 2)

def send_whatsapp_message(phone, message):
    """Send WhatsApp message using WhatsApp Business API"""
    try:
        # Get WhatsApp API credentials from environment
        api_token = os.environ.get('WHATSAPP_API_TOKEN', 'demo_token')
        phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'demo_id')
        
        # Format phone number (remove any formatting)
        clean_phone = ''.join(filter(str.isdigit, phone))
        if clean_phone.startswith('504'):
            formatted_phone = clean_phone
        else:
            formatted_phone = f"504{clean_phone}"
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": formatted_phone,
            "type": "text",
            "text": {"body": message}
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
        
    except Exception as e:
        return False, str(e)

def get_available_time_slots(date, service_duration=30):
    """Get available time slots for a given date"""
    from models import Appointment
    
    # Business hours: 8 AM to 6 PM
    start_hour = 8
    end_hour = 18
    
    available_slots = []
    current_time = datetime.combine(date, datetime.min.time().replace(hour=start_hour))
    end_time = datetime.combine(date, datetime.min.time().replace(hour=end_hour))
    
    # Get existing appointments for the date
    existing_appointments = Appointment.query.filter(
        func.date(Appointment.appointment_date) == date,
        Appointment.status == 'scheduled'
    ).all()
    
    while current_time < end_time:
        # Check if this slot is available
        slot_end = current_time + timedelta(minutes=service_duration)
        is_available = True
        
        for appointment in existing_appointments:
            app_end = appointment.appointment_date + timedelta(minutes=appointment.service_type.duration_minutes)
            if (current_time < app_end and slot_end > appointment.appointment_date):
                is_available = False
                break
        
        if is_available:
            available_slots.append(current_time.strftime("%H:%M"))
        
        current_time += timedelta(minutes=30)  # 30-minute intervals
    
    return available_slots

def perform_cash_closing(actual_cash_data, notes=""):
    """Perform end-of-day cash closing"""
    today = datetime.now().date()
    
    # Check if closing already exists for today
    existing_closing = CashClosing.query.filter_by(closing_date=today).first()
    if existing_closing:
        return False, "Ya se realizó el cierre de caja para el día de hoy"
    
    # Calculate sales for today
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    sales_total = db.session.query(func.sum(Invoice.total_amount)).filter(
        Invoice.created_at.between(today_start, today_end),
        Invoice.payment_method == 'efectivo'
    ).scalar() or 0.0
    
    # Get opening amount (from previous day's closing or default)
    yesterday = today - timedelta(days=1)
    previous_closing = CashClosing.query.filter_by(closing_date=yesterday).first()
    opening_amount = previous_closing.actual_amount if previous_closing else 0.0
    
    # Calculate expected amount
    expected_amount = opening_amount + sales_total
    
    # Calculate actual amount from cash counts
    actual_amount = calculate_cash_total(actual_cash_data)
    
    # Calculate difference
    difference = actual_amount - expected_amount
    
    # Create cash closing record
    cash_closing = CashClosing(
        closing_date=today,
        opening_amount=opening_amount,
        sales_amount=sales_total,
        expected_amount=expected_amount,
        actual_amount=actual_amount,
        difference=difference,
        notes=notes,
        **actual_cash_data
    )
    
    db.session.add(cash_closing)
    db.session.commit()
    
    return True, cash_closing

def update_customer_crm(customer_id):
    """Update CRM data for customer"""
    customer = Customer.query.get(customer_id)
    if customer:
        customer.last_visit = datetime.utcnow()
        customer.total_visits = customer.total_visits + 1 if customer.total_visits else 1
        db.session.commit()
