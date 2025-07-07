import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "carwash_secret_key_2025")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Make csrf_token available in templates
from flask_wtf.csrf import generate_csrf
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///carwash.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models and routes
    import models
    import routes
    
    # Create all tables
    db.create_all()
    
    # Initialize sample service types if none exist
    from models import ServiceType
    if not ServiceType.query.first():
        default_services = [
            ServiceType(name="Lavado Básico", price=150.00, category="lavado"),
            ServiceType(name="Lavado Premium", price=250.00, category="lavado"),
            ServiceType(name="Encerado", price=200.00, category="lavado"),
            ServiceType(name="Cambio de Aceite", price=300.00, category="servicio"),
            ServiceType(name="Filtro de Aire", price=150.00, category="accesorio"),
            ServiceType(name="Ambientador", price=50.00, category="accesorio")
        ]
        for service in default_services:
            db.session.add(service)
        db.session.commit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
