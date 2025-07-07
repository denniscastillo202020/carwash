from app import db
from datetime import datetime
from sqlalchemy import func

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_visit = db.Column(db.DateTime)
    total_visits = db.Column(db.Integer, default=1)
    
    # Relationships
    invoices = db.relationship('Invoice', backref='customer', lazy=True)
    appointments = db.relationship('Appointment', backref='customer', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    barcode = db.Column(db.String(50), unique=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50), nullable=False)  # lavado, accesorio, servicio
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    invoice_items = db.relationship('InvoiceItem', backref='product', lazy=True)

class ServiceType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # lavado, accesorio, servicio
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, default=30)
    
    # Relationships
    invoice_items = db.relationship('InvoiceItem', backref='service_type', lazy=True)
    appointments = db.relationship('Appointment', backref='service_type', lazy=True)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(20), default='efectivo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='paid')
    
    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    cash_register_entry = db.relationship('CashRegisterEntry', backref='invoice', uselist=False)

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    service_type_id = db.Column(db.Integer, db.ForeignKey('service_type.id'))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))

class CashRegisterEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), unique=True)
    # Denominations in Lempiras
    bills_1000 = db.Column(db.Integer, default=0)
    bills_500 = db.Column(db.Integer, default=0)
    bills_200 = db.Column(db.Integer, default=0)
    bills_100 = db.Column(db.Integer, default=0)
    bills_50 = db.Column(db.Integer, default=0)
    bills_20 = db.Column(db.Integer, default=0)
    bills_10 = db.Column(db.Integer, default=0)
    bills_5 = db.Column(db.Integer, default=0)
    bills_2 = db.Column(db.Integer, default=0)
    bills_1 = db.Column(db.Integer, default=0)
    # Coins
    coins_50c = db.Column(db.Integer, default=0)
    coins_20c = db.Column(db.Integer, default=0)
    coins_10c = db.Column(db.Integer, default=0)
    coins_5c = db.Column(db.Integer, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    service_type_id = db.Column(db.Integer, db.ForeignKey('service_type.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    whatsapp_message_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CashClosing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    closing_date = db.Column(db.Date, nullable=False)
    opening_amount = db.Column(db.Float, default=0.0)
    sales_amount = db.Column(db.Float, nullable=False)
    expected_amount = db.Column(db.Float, nullable=False)
    actual_amount = db.Column(db.Float, nullable=False)
    difference = db.Column(db.Float, nullable=False)
    # Total bills and coins count
    total_bills_1000 = db.Column(db.Integer, default=0)
    total_bills_500 = db.Column(db.Integer, default=0)
    total_bills_200 = db.Column(db.Integer, default=0)
    total_bills_100 = db.Column(db.Integer, default=0)
    total_bills_50 = db.Column(db.Integer, default=0)
    total_bills_20 = db.Column(db.Integer, default=0)
    total_bills_10 = db.Column(db.Integer, default=0)
    total_bills_5 = db.Column(db.Integer, default=0)
    total_bills_2 = db.Column(db.Integer, default=0)
    total_bills_1 = db.Column(db.Integer, default=0)
    total_coins_50c = db.Column(db.Integer, default=0)
    total_coins_20c = db.Column(db.Integer, default=0)
    total_coins_10c = db.Column(db.Integer, default=0)
    total_coins_5c = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
