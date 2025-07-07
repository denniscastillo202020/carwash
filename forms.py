from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, TextAreaField, DateTimeField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, Email
from wtforms.widgets import DateTimeInput

class CustomerForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Teléfono', validators=[DataRequired(), Length(min=8, max=20)])
    email = StringField('Email', validators=[Optional(), Email()])
    address = TextAreaField('Dirección', validators=[Optional(), Length(max=200)])

class ProductForm(FlaskForm):
    name = StringField('Nombre del Producto', validators=[DataRequired(), Length(min=2, max=100)])
    barcode = StringField('Código de Barras', validators=[Optional(), Length(max=50)])
    price = FloatField('Precio (L)', validators=[DataRequired(), NumberRange(min=0.01)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Categoría', choices=[
        ('lavado', 'Lavado'),
        ('accesorio', 'Accesorio'),
        ('servicio', 'Servicio')
    ], validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])

class ServiceTypeForm(FlaskForm):
    name = StringField('Nombre del Servicio', validators=[DataRequired(), Length(min=2, max=100)])
    price = FloatField('Precio (L)', validators=[DataRequired(), NumberRange(min=0.01)])
    category = SelectField('Categoría', choices=[
        ('lavado', 'Lavado'),
        ('accesorio', 'Accesorio'),
        ('servicio', 'Servicio')
    ], validators=[DataRequired()])
    duration_minutes = IntegerField('Duración (minutos)', validators=[DataRequired(), NumberRange(min=5, max=480)])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])

class InvoiceForm(FlaskForm):
    customer_id = HiddenField('Customer ID')
    customer_name = StringField('Nombre del Cliente', validators=[DataRequired()])
    customer_phone = StringField('Teléfono', validators=[DataRequired()])
    customer_email = StringField('Email', validators=[Optional(), Email()])
    customer_address = TextAreaField('Dirección', validators=[Optional()])
    payment_method = SelectField('Método de Pago', choices=[
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia')
    ], default='efectivo')

class CashRegisterForm(FlaskForm):
    # Bills

    bills_500 = IntegerField('Billetes L500', validators=[NumberRange(min=0)], default=0)
    bills_200 = IntegerField('Billetes L200', validators=[NumberRange(min=0)], default=0)
    bills_100 = IntegerField('Billetes L100', validators=[NumberRange(min=0)], default=0)
    bills_50 = IntegerField('Billetes L50', validators=[NumberRange(min=0)], default=0)
    bills_20 = IntegerField('Billetes L20', validators=[NumberRange(min=0)], default=0)
    bills_10 = IntegerField('Billetes L10', validators=[NumberRange(min=0)], default=0)
    bills_5 = IntegerField('Billetes L5', validators=[NumberRange(min=0)], default=0)
    bills_2 = IntegerField('Billetes L2', validators=[NumberRange(min=0)], default=0)
    bills_1 = IntegerField('Billetes L1', validators=[NumberRange(min=0)], default=0)
    # Coins
    coins_50c = IntegerField('Monedas 50c', validators=[NumberRange(min=0)], default=0)
    coins_20c = IntegerField('Monedas 20c', validators=[NumberRange(min=0)], default=0)
    coins_10c = IntegerField('Monedas 10c', validators=[NumberRange(min=0)], default=0)
    coins_5c = IntegerField('Monedas 5c', validators=[NumberRange(min=0)], default=0)

class AppointmentForm(FlaskForm):
    customer_name = StringField('Nombre del Cliente', validators=[DataRequired()])
    customer_phone = StringField('Teléfono', validators=[DataRequired()])
    service_type_id = SelectField('Tipo de Servicio', coerce=int, validators=[DataRequired()])
    appointment_date = DateTimeField('Fecha y Hora', validators=[DataRequired()], widget=DateTimeInput())
    notes = TextAreaField('Notas', validators=[Optional(), Length(max=500)])
