from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from app import app, db
from models import Customer, Product, ServiceType, Invoice, InvoiceItem, CashRegisterEntry, Appointment, CashClosing
from forms import CustomerForm, ProductForm, ServiceTypeForm, InvoiceForm, CashRegisterForm, AppointmentForm
from utils import (generate_invoice_number, format_lempiras, calculate_cash_total, 
                   send_whatsapp_message, get_available_time_slots, perform_cash_closing, update_customer_crm)
from datetime import datetime, date, timedelta
from sqlalchemy import func, or_
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import io

@app.route('/')
def index():
    """Dashboard with key metrics"""
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Today's metrics
    today_sales = db.session.query(func.sum(Invoice.total_amount)).filter(
        Invoice.created_at.between(today_start, today_end)
    ).scalar() or 0.0
    
    today_invoices = Invoice.query.filter(
        Invoice.created_at.between(today_start, today_end)
    ).count()
    
    today_appointments = Appointment.query.filter(
        func.date(Appointment.appointment_date) == today,
        Appointment.status == 'scheduled'
    ).count()
    
    # Low stock products
    low_stock_products = Product.query.filter(Product.stock <= 5).all()
    
    # Recent customers
    recent_customers = Customer.query.order_by(Customer.created_at.desc()).limit(5).all()
    
    return render_template('enhanced_index.html',
                         daily_sales=today_sales,
                         daily_invoices=today_invoices,
                         daily_appointments=today_appointments,
                         monthly_invoices=today_invoices * 30,
                         monthly_sales=today_sales * 30,
                         total_customers=Customer.query.count(),
                         new_customers_month=0,
                         pending_appointments=today_appointments,
                         recent_invoices=[],
                         today_appointments=[],
                         low_stock_products=low_stock_products)

@app.route('/inventory')
def inventory():
    """Inventory management"""
    products = Product.query.all()
    services = ServiceType.query.all()
    return render_template('inventory.html', products=products, services=services)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    """Add new product"""
    form = ProductForm()
    if form.validate_on_submit():
        # Check if barcode already exists
        if form.barcode.data and Product.query.filter_by(barcode=form.barcode.data).first():
            flash('El código de barras ya existe', 'error')
            return render_template('inventory.html', form=form)
        
        product = Product(
            name=form.name.data,
            barcode=form.barcode.data,
            price=form.price.data,
            stock=form.stock.data,
            category=form.category.data,
            description=form.description.data
        )
        
        db.session.add(product)
        db.session.commit()
        flash('Producto agregado exitosamente', 'success')
        return redirect(url_for('inventory'))
    
    # If form validation fails, re-render with product list
    products = Product.query.all()
    services = ServiceType.query.all()
    return render_template('inventory.html', products=products, services=services, form=form)

@app.route('/add_service', methods=['GET', 'POST'])
def add_service():
    """Add new service type"""
    form = ServiceTypeForm()
    if form.validate_on_submit():
        service = ServiceType(
            name=form.name.data,
            price=form.price.data,
            category=form.category.data,
            duration_minutes=form.duration_minutes.data,
            description=form.description.data
        )
        
        db.session.add(service)
        db.session.commit()
        flash('Servicio agregado exitosamente', 'success')
        return redirect(url_for('inventory'))
    
    # If form validation fails, re-render with service list
    products = Product.query.all()
    services = ServiceType.query.all()
    return render_template('inventory.html', products=products, services=services, form=form)

@app.route('/customers')
def customers():
    """Customer management (CRM)"""
    search = request.args.get('search', '')
    if search:
        customers_list = Customer.query.filter(
            or_(Customer.name.contains(search),
                Customer.phone.contains(search),
                Customer.email.contains(search))
        ).order_by(Customer.created_at.desc()).all()
    else:
        customers_list = Customer.query.order_by(Customer.created_at.desc()).all()
    
    return render_template('customers.html', customers=customers_list, search=search)

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    """Add new customer"""
    form = CustomerForm()
    if form.validate_on_submit():
        # Check if customer already exists
        existing_customer = Customer.query.filter_by(phone=form.phone.data).first()
        if existing_customer:
            flash('Ya existe un cliente con este número de teléfono', 'error')
            return render_template('customers.html', form=form)
        
        customer = Customer(
            name=form.name.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data
        )
        
        db.session.add(customer)
        db.session.commit()
        flash('Cliente agregado exitosamente', 'success')
        return redirect(url_for('customers'))
    
    # If form validation fails, re-render with customers list
    customers_list = Customer.query.order_by(Customer.created_at.desc()).all()
    return render_template('customers.html', customers=customers_list, form=form)

@app.route('/invoice')
def invoice():
    """Invoice creation"""
    products = Product.query.filter(Product.stock > 0).all()
    services = ServiceType.query.all()
    return render_template('invoice.html', products=products, services=services)

@app.route('/create_invoice', methods=['POST'])
def create_invoice():
    """Create new invoice"""
    try:
        # Get customer data
        customer_name = request.form.get('customer_name', '').strip()
        customer_phone = request.form.get('customer_phone', '').strip()
        customer_email = request.form.get('customer_email', '').strip()
        customer_address = request.form.get('customer_address', '').strip()
        payment_method = request.form.get('payment_method', 'efectivo')
        
        if not customer_name or not customer_phone:
            flash('Nombre y teléfono del cliente son obligatorios', 'error')
            return redirect(url_for('invoice'))
        
        # Find or create customer
        customer = Customer.query.filter_by(phone=customer_phone).first()
        if not customer:
            customer = Customer(
                name=customer_name,
                phone=customer_phone,
                email=customer_email,
                address=customer_address
            )
            db.session.add(customer)
            db.session.flush()  # Get customer ID
        else:
            # Update customer info if needed
            customer.name = customer_name
            customer.email = customer_email or customer.email
            customer.address = customer_address or customer.address
        
        # Create invoice
        invoice = Invoice(
            invoice_number=generate_invoice_number(),
            customer_id=customer.id,
            total_amount=0.0,
            payment_method=payment_method
        )
        db.session.add(invoice)
        db.session.flush()  # Get invoice ID
        
        # Process items
        total_amount = 0.0
        items_processed = False
        
        # Products
        for key in request.form:
            if key.startswith('product_quantity_'):
                product_id = key.split('_')[-1]
                quantity = int(request.form.get(key, 0))
                
                if quantity > 0:
                    product = Product.query.get(product_id)
                    if product and product.stock >= quantity:
                        item_total = product.price * quantity
                        
                        invoice_item = InvoiceItem(
                            invoice_id=invoice.id,
                            product_id=product.id,
                            quantity=quantity,
                            unit_price=product.price,
                            total_price=item_total,
                            description=product.name
                        )
                        db.session.add(invoice_item)
                        
                        # Update stock
                        product.stock -= quantity
                        total_amount += item_total
                        items_processed = True
        
        # Services
        for key in request.form:
            if key.startswith('service_quantity_'):
                service_id = key.split('_')[-1]
                quantity = int(request.form.get(key, 0))
                
                if quantity > 0:
                    service = ServiceType.query.get(service_id)
                    if service:
                        item_total = service.price * quantity
                        
                        invoice_item = InvoiceItem(
                            invoice_id=invoice.id,
                            service_type_id=service.id,
                            quantity=quantity,
                            unit_price=service.price,
                            total_price=item_total,
                            description=service.name
                        )
                        db.session.add(invoice_item)
                        total_amount += item_total
                        items_processed = True
        
        if not items_processed:
            flash('Debe agregar al menos un producto o servicio', 'error')
            db.session.rollback()
            return redirect(url_for('invoice'))
        
        # Update invoice total
        invoice.total_amount = total_amount
        
        # If payment is cash, redirect to cash register
        if payment_method == 'efectivo':
            db.session.commit()
            return redirect(url_for('cash_register', invoice_id=invoice.id))
        
        # Update customer CRM
        update_customer_crm(customer.id)
        
        db.session.commit()
        flash(f'Factura {invoice.invoice_number} creada exitosamente', 'success')
        return redirect(url_for('print_invoice', invoice_id=invoice.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear factura: {str(e)}', 'error')
        return redirect(url_for('invoice'))

@app.route('/cash_register/<int:invoice_id>')
def cash_register(invoice_id):
    """Cash register for invoice payment"""
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('cash_register.html', invoice=invoice, format_lempiras=format_lempiras)

@app.route('/process_cash_payment/<int:invoice_id>', methods=['POST'])
def process_cash_payment(invoice_id):
    """Process cash payment with denominations"""
    invoice = Invoice.query.get_or_404(invoice_id)
    form = CashRegisterForm()
    
    if form.validate_on_submit():
        # Calculate total from denominations
        cash_data = {
            'bills_1000': form.bills_1000.data,
            'bills_500': form.bills_500.data,
            'bills_200': form.bills_200.data,
            'bills_100': form.bills_100.data,
            'bills_50': form.bills_50.data,
            'bills_20': form.bills_20.data,
            'bills_10': form.bills_10.data,
            'bills_5': form.bills_5.data,
            'bills_2': form.bills_2.data,
            'bills_1': form.bills_1.data,
            'coins_50c': form.coins_50c.data,
            'coins_20c': form.coins_20c.data,
            'coins_10c': form.coins_10c.data,
            'coins_5c': form.coins_5c.data,
        }
        
        total_received = calculate_cash_total(cash_data)
        
        if total_received < invoice.total_amount:
            flash(f'Cantidad insuficiente. Se requieren {format_lempiras(invoice.total_amount)}', 'error')
            return render_template('cash_register.html', invoice=invoice, form=form, format_lempiras=format_lempiras)
        
        # Record cash register entry
        cash_entry = CashRegisterEntry(
            invoice_id=invoice.id,
            total_amount=total_received,
            **cash_data
        )
        db.session.add(cash_entry)
        
        # Update customer CRM
        update_customer_crm(invoice.customer_id)
        
        db.session.commit()
        
        change = total_received - invoice.total_amount
        if change > 0:
            flash(f'Pago procesado. Cambio: {format_lempiras(change)}', 'success')
        else:
            flash('Pago procesado exitosamente', 'success')
        
        return redirect(url_for('print_invoice', invoice_id=invoice.id))
    
    return render_template('cash_register.html', invoice=invoice, form=form, format_lempiras=format_lempiras)

@app.route('/cash_closing')
def cash_closing():
    """Daily cash closing"""
    today = datetime.now().date()
    existing_closing = CashClosing.query.filter_by(closing_date=today).first()
    
    # Calculate today's sales
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    today_sales = db.session.query(func.sum(Invoice.total_amount)).filter(
        Invoice.created_at.between(today_start, today_end),
        Invoice.payment_method == 'efectivo'
    ).scalar() or 0.0
    
    # Get cash entries for today
    cash_entries = CashRegisterEntry.query.join(Invoice).filter(
        Invoice.created_at.between(today_start, today_end)
    ).all()
    
    return render_template('cash_register.html', 
                         closing_mode=True,
                         existing_closing=existing_closing,
                         today_sales=today_sales,
                         cash_entries=cash_entries,
                         format_lempiras=format_lempiras)

@app.route('/perform_cash_closing', methods=['POST'])
def perform_cash_closing_route():
    """Perform daily cash closing"""
    form = CashRegisterForm()
    
    if form.validate_on_submit():
        cash_data = {
            'total_bills_1000': form.bills_1000.data,
            'total_bills_500': form.bills_500.data,
            'total_bills_200': form.bills_200.data,
            'total_bills_100': form.bills_100.data,
            'total_bills_50': form.bills_50.data,
            'total_bills_20': form.bills_20.data,
            'total_bills_10': form.bills_10.data,
            'total_bills_5': form.bills_5.data,
            'total_bills_2': form.bills_2.data,
            'total_bills_1': form.bills_1.data,
            'total_coins_50c': form.coins_50c.data,
            'total_coins_20c': form.coins_20c.data,
            'total_coins_10c': form.coins_10c.data,
            'total_coins_5c': form.coins_5c.data,
        }
        
        notes = request.form.get('notes', '')
        success, result = perform_cash_closing(cash_data, notes)
        
        if success:
            flash(f'Cierre de caja realizado. Diferencia: {format_lempiras(result.difference)}', 'success')
        else:
            flash(result, 'error')
    
    return redirect(url_for('cash_closing'))

@app.route('/appointments')
def appointments():
    """Appointment management"""
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    
    # Get appointments for selected date
    appointments_list = Appointment.query.filter(
        func.date(Appointment.appointment_date) == selected_date_obj
    ).order_by(Appointment.appointment_date).all()
    
    services = ServiceType.query.all()
    
    return render_template('appointments.html', 
                         appointments=appointments_list,
                         services=services,
                         selected_date=selected_date)

@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    """Add new appointment"""
    form = AppointmentForm()
    form.service_type_id.choices = [(s.id, s.name) for s in ServiceType.query.all()]
    
    if form.validate_on_submit():
        # Find or create customer
        customer = Customer.query.filter_by(phone=form.customer_phone.data).first()
        if not customer:
            customer = Customer(
                name=form.customer_name.data,
                phone=form.customer_phone.data
            )
            db.session.add(customer)
            db.session.flush()
        
        appointment = Appointment(
            customer_id=customer.id,
            service_type_id=form.service_type_id.data,
            appointment_date=form.appointment_date.data,
            notes=form.notes.data
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Send WhatsApp confirmation
        service = ServiceType.query.get(form.service_type_id.data)
        message = f"""¡Hola {customer.name}!
        
Tu cita ha sido confirmada:
📅 Fecha: {appointment.appointment_date.strftime('%d/%m/%Y %H:%M')}
🚗 Servicio: {service.name}
💰 Precio: {format_lempiras(service.price)}

¡Te esperamos en nuestro car wash!

Ubicación: Peña Blanca, Cortés
Teléfono: 97164446"""
        
        success, response = send_whatsapp_message(customer.phone, message)
        if success:
            flash('Cita creada y confirmación enviada por WhatsApp', 'success')
        else:
            flash('Cita creada, pero no se pudo enviar WhatsApp', 'warning')
        
        return redirect(url_for('appointments'))
    
    flash('Error al crear la cita', 'error')
    return redirect(url_for('appointments'))

@app.route('/api/available_slots')
def api_available_slots():
    """API endpoint for available time slots"""
    date_str = request.args.get('date')
    service_id = request.args.get('service_id')
    
    if not date_str or not service_id:
        return jsonify({'error': 'Date and service_id required'}), 400
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        service = ServiceType.query.get(service_id)
        
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        slots = get_available_time_slots(date_obj, service.duration_minutes)
        return jsonify({'slots': slots})
        
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

@app.route('/search_customer')
def search_customer():
    """Search customer by phone for autocomplete"""
    phone = request.args.get('phone', '')
    if len(phone) >= 4:
        customer = Customer.query.filter_by(phone=phone).first()
        if customer:
            return jsonify({
                'found': True,
                'name': customer.name,
                'email': customer.email or '',
                'address': customer.address or '',
                'total_visits': customer.total_visits or 0
            })
    
    return jsonify({'found': False})

@app.route('/search_product')
def search_product():
    """Search product by barcode"""
    barcode = request.args.get('barcode', '')
    if barcode:
        product = Product.query.filter_by(barcode=barcode).first()
        if product:
            return jsonify({
                'found': True,
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'stock': product.stock
            })
    
    return jsonify({'found': False})

@app.route('/print_invoice/<int:invoice_id>')
def print_invoice(invoice_id):
    """Thermal invoice printing view"""
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('print_invoice.html', invoice=invoice, format_lempiras=format_lempiras)

@app.route('/export_invoices')
def export_invoices():
    """Export daily invoices to Excel"""
    export_date = request.args.get('date')
    if export_date:
        export_date = datetime.strptime(export_date, '%Y-%m-%d').date()
    else:
        export_date = datetime.now().date()
    
    # Get invoices for the specified date
    start_date = datetime.combine(export_date, datetime.min.time())
    end_date = datetime.combine(export_date, datetime.max.time())
    
    invoices = Invoice.query.filter(
        Invoice.created_at.between(start_date, end_date)
    ).order_by(Invoice.created_at.desc()).all()
    
    # Create Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Facturas {export_date.strftime('%Y-%m-%d')}"
    
    # Header styling
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    center_alignment = Alignment(horizontal="center", vertical="center")
    
    # Company header
    ws.merge_cells('A1:H1')
    ws['A1'] = "Car Wash Peña Blanca - Reporte de Facturas"
    ws['A1'].font = Font(bold=True, size=16)
    ws['A1'].alignment = center_alignment
    
    ws.merge_cells('A2:H2')
    ws['A2'] = f"Fecha: {export_date.strftime('%d/%m/%Y')} | Peña Blanca, Cortés | Tel: 97164446"
    ws['A2'].font = Font(size=12)
    ws['A2'].alignment = center_alignment
    
    # Column headers
    headers = ['Factura', 'Cliente', 'Teléfono', 'Total', 'Método', 'Fecha', 'Hora', 'Items']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_alignment
    
    # Data rows
    row_num = 5
    total_sales = 0
    
    for invoice in invoices:
        # Invoice items summary
        items_summary = ', '.join([f"{item.description or (item.product.name if item.product else item.service_type.name)} ({item.quantity})" 
                                 for item in invoice.items])
        
        ws.cell(row=row_num, column=1, value=invoice.invoice_number)
        ws.cell(row=row_num, column=2, value=invoice.customer.name)
        ws.cell(row=row_num, column=3, value=invoice.customer.phone)
        ws.cell(row=row_num, column=4, value=invoice.total_amount)
        ws.cell(row=row_num, column=5, value=invoice.payment_method.title())
        ws.cell(row=row_num, column=6, value=invoice.created_at.strftime('%d/%m/%Y'))
        ws.cell(row=row_num, column=7, value=invoice.created_at.strftime('%H:%M'))
        ws.cell(row=row_num, column=8, value=items_summary)
        
        # Format currency
        ws.cell(row=row_num, column=4).number_format = 'L #,##0.00'
        
        total_sales += invoice.total_amount
        row_num += 1
    
    # Summary row
    if invoices:
        row_num += 1
        ws.merge_cells(f'A{row_num}:C{row_num}')
        summary_cell = ws.cell(row=row_num, column=1, value="TOTAL DEL DÍA:")
        summary_cell.font = Font(bold=True)
        summary_cell.alignment = Alignment(horizontal="right")
        
        total_cell = ws.cell(row=row_num, column=4, value=total_sales)
        total_cell.font = Font(bold=True)
        total_cell.number_format = 'L #,##0.00'
        total_cell.fill = PatternFill(start_color="FFE699", end_color="FFE699", fill_type="solid")
    
    # Adjust column widths
    column_widths = [15, 25, 15, 12, 12, 12, 8, 40]
    for col, width in enumerate(column_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = width
    
    # Save to BytesIO
    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    filename = f"facturas_carwash_{export_date.strftime('%Y%m%d')}.xlsx"
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@app.context_processor
def utility_processor():
    """Make utility functions available in templates"""
    return dict(format_lempiras=format_lempiras, datetime=datetime)
