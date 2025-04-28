# Inventory Management System

A modern, scalable inventory management system built with FastAPI, PostgreSQL, and WebSocket support.

## Features

- Real-time inventory updates using WebSockets
- Product management (CRUD operations)
- Inventory tracking
- Supplier management
- Transaction processing with Stripe integration
- RESTful API with OpenAPI documentation
- PostgreSQL database integration

## Tech Stack

- FastAPI (Python web framework)
- PostgreSQL (Database)
- SQLAlchemy (ORM)
- Pydantic (Data validation)
- Stripe (Payment processing)
- WebSockets (Real-time updates)
- Redis (WebSocket message queue)

## Directory Structure

```
app/
├── __init__.py
├── core/
│   ├── config.py
│   └── database.py
├── models/
│   ├── product.py
│   ├── inventory.py
│   ├── supplier.py
│   ├── transaction.py
│   └── user.py
├── routes/
│   ├── product_routes.py
│   ├── inventory_routes.py
│   ├── supplier_routes.py
│   ├── transaction_routes.py
│   └── auth.py
├── schemas/
│   ├── product.py
│   ├── inventory.py
│   ├── supplier.py
│   └── transaction.py
├── services/
│   ├── product_service.py
│   ├── inventory_service.py
│   ├── payment_service.py
│   └── websocket_service.py
└── run.py
```

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd inventory-management-system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL:
- Install PostgreSQL
- Create a database named 'inventory_db'
- The default credentials are:
  - Username: postgres
  - Password: admin
  - Database: inventory_db

5. Set up environment variables:
```bash
export STRIPE_API_KEY="your-stripe-api-key"
export STRIPE_WEBHOOK_SECRET="your-stripe-webhook-secret"
```

6. Initialize the database:
```bash
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

7. Run the application:
```bash
uvicorn app.run:app --reload
```

The application will be available at http://localhost:8000

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## WebSocket Support

The application supports real-time updates through WebSocket connections. Connect to:
```
ws://localhost:8000/api/v1/products/ws
```

## Testing

Run the tests using pytest:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.