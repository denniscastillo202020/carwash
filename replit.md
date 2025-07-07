# Car Wash Peña Blanca - Sistema de Gestión

## Overview

Car Wash Peña Blanca is a comprehensive Point of Sale (POS) and Customer Relationship Management (CRM) system designed specifically for the car wash business in Peña Blanca, Cortés, Honduras. The system handles customer management, inventory tracking, service scheduling, invoicing, and cash register operations with support for Lempiras currency and WhatsApp integration for appointments.

**Business Information:**
- Name: Car Wash Peña Blanca  
- Phone: 9464-8987
- Location: Peña Blanca, Cortés, Honduras
- Logo: Integrated custom logo with red Mercedes-Benz car and soap bubbles design

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite (configurable to PostgreSQL via DATABASE_URL)
- **Session Management**: Flask-WTF for CSRF protection and form handling
- **Deployment**: WSGI-compatible with ProxyFix middleware for reverse proxy support

### Frontend Architecture
- **UI Framework**: Bootstrap 5 for responsive design
- **Icons**: Font Awesome 6.4.0 for comprehensive iconography
- **JavaScript**: Vanilla JS with modular component architecture
- **Styling**: Custom CSS with CSS variables for theming

### Database Schema
- **Customer Management**: Customer table with CRM features (visit tracking, contact info)
- **Inventory Management**: Product and ServiceType tables for items and services
- **Financial Operations**: Invoice, InvoiceItem, CashRegisterEntry, CashClosing tables
- **Scheduling**: Appointment table for WhatsApp-based scheduling

## Key Components

### Core Models
1. **Customer**: CRM functionality with visit tracking and contact management
2. **Product**: Inventory items with barcode support and stock management
3. **ServiceType**: Car wash services with duration and pricing
4. **Invoice**: Financial transactions with tax calculations
5. **Appointment**: WhatsApp-based scheduling system
6. **CashRegister**: Cash management with denomination tracking

### Business Logic
- **Invoice Generation**: Automatic invoice numbering with date-based prefixes
- **Customer CRM**: Automatic visit tracking and customer history
- **Cash Management**: Detailed cash register with denomination counting
- **WhatsApp Integration**: Appointment scheduling via WhatsApp API
- **Inventory Control**: Stock tracking with low-stock alerts

### User Interface
- **Dashboard**: Real-time metrics for daily sales, invoices, and appointments
- **POS System**: Complete invoicing with customer lookup and payment processing
- **Inventory Management**: Dual-tab interface for products and services
- **CRM System**: Customer search, history, and communication tools
- **Cash Register**: Physical cash counting interface with closing procedures

## Data Flow

### Invoice Creation Process
1. Customer lookup by phone number (existing customer detection)
2. Item/service selection with real-time pricing
3. Tax calculation and total computation
4. Payment method selection
5. Invoice generation with unique numbering
6. Thermal printer-optimized receipt generation
7. Customer CRM update (visit tracking)

### Appointment Scheduling
1. WhatsApp integration for customer communication
2. Time slot availability checking
3. Service duration-based scheduling
4. Automatic customer creation/update
5. Appointment confirmation via WhatsApp

### Cash Register Operations
1. Real-time cash tracking with denomination input
2. Invoice payment processing
3. End-of-day cash closing procedures
4. Variance tracking and reporting

## External Dependencies

### Frontend Libraries
- Bootstrap 5.3.0 (CSS framework)
- Font Awesome 6.4.0 (icon library)

### Python Packages
- Flask (web framework)
- Flask-SQLAlchemy (ORM)
- Flask-WTF (form handling)
- Werkzeug (WSGI utilities)

### Third-party Integrations
- WhatsApp Business API (appointment scheduling)
- Thermal printer support (receipt printing)

## Deployment Strategy

### Environment Configuration
- **Database**: Configurable via DATABASE_URL environment variable
- **Security**: Session secret via SESSION_SECRET environment variable
- **Production**: WSGI-compatible with proxy support

### Database Migration
- Automatic table creation on first run
- Sample data initialization for service types
- SQLite for development, PostgreSQL production-ready

### Scaling Considerations
- Connection pooling configured for database efficiency
- Modular component architecture for feature expansion
- Responsive design for mobile device support

## Changelog
- July 07, 2025: Initial setup
- July 07, 2025: Phone number updated to 97164446
- July 07, 2025: CSRF tokens added to all forms to fix saving issues
- July 07, 2025: Enhanced dashboard with comprehensive metrics and Excel export
- July 07, 2025: Invoice preview functionality with cash payment denominations tracking
- July 07, 2025: Excel export feature for daily invoice backup implemented
- July 07, 2025: Successfully migrated from Replit Agent to standard environment
- July 07, 2025: Fixed CSRF token errors causing internal server errors
- July 07, 2025: Added PostgreSQL database for production deployment

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Issues Fixed
- ✓ Customers not saving - Fixed CSRF token issues
- ✓ Products not saving - Fixed CSRF token issues  
- ✓ Invoices not generating - Fixed CSRF token issues
- ✓ Appointments not saving - Fixed CSRF token issues
- ✓ Dashboard too simple - Enhanced with detailed metrics
- ✓ No invoice preview - Added preview modal
- ✓ No cash denomination tracking - Added cash payment modal with bill/coin counting
- ✓ No Excel export - Added daily invoice export feature
- ✓ Phone number correction - Updated to 97164446 throughout system
- ✓ Complex invoicing system - Simplified to 3-column layout
- ✓ JavaScript errors - Removed complex scripts, made simple validation
- ✓ Cash register automation - Auto-calculates totals and change
- ✓ Cash closing incomplete - Shows sales by payment method with bill denominations
- ✓ Power BI Analytics - Added comprehensive analytics dashboard with charts and KPIs
- ✓ Logo in invoices - Added business logo to thermal receipt format
- ✓ Dashboard customization - Added background personalization options
- ✓ Auto-refresh analytics - System updates data every 5 minutes automatically
- ✓ Excel exports - All cash closings and analytics export to Excel automatically
- ✓ Simplified appointments - Streamlined single-form appointment scheduling
- ✓ WhatsApp bot integration - Automated responses for availability and confirmations
- ✓ Ready notifications - One-click customer notifications when service is complete