# 🌾 Rice Mill Management System

![Dashboard Preview](static/core/img/dashboard-preview.png)

## 📝 Table of Contents
- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Installation Guide](#-installation-guide)
- [System Architecture](#-system-architecture)
- [User Roles](#-user-roles)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

## 🌟 Project Overview

The Rice Mill Management System is a comprehensive Django web application designed to streamline operations for rice milling businesses. This system digitizes and automates key processes including paddy procurement, milling operations, inventory management, order processing, and delivery logistics.

Built with modern web technologies, the application features role-based access control, real-time dashboards, and comprehensive reporting capabilities to help mill operators optimize their workflow and improve operational efficiency.

## 🚀 Key Features

### 🌐 Core Functionalities
- **Multi-role Authentication System** with 5 distinct user types
- **Interactive Dashboards** tailored for each user role
- **Paddy Supply Tracking** from procurement to processing
- **Inventory Management** for rice products and by-products
- **Order Processing** with integrated delivery system
- **Payment Tracking** for both farmers and customers

### 📊 Dashboard Highlights
- Real-time processing metrics for mill operators
- Delivery tracking system for logistics personnel
- Sales analytics for administrators
- Farmer payment history and supply records
- Customer order history and preferences

### 🔒 Security Features
- Password encryption and secure authentication
- Role-based permission system
- CSRF protection and secure headers
- Audit logging for sensitive operations

## 💻 Technology Stack

### Backend
- **Python 3.9+**
- **Django 4.0** (Web Framework)
- **sqlite3** (Database)
- **Redis** (Caching)
- **Celery** (Task Queue)

### Frontend
- **HTML5**, **CSS3**, **JavaScript**
- **Bootstrap 5** (UI Framework)
- **Chart.js** (Data Visualization)
- **Font Awesome** (Icons)

### DevOps
- **Docker** (Containerization)
- **Nginx** (Web Server)
- **Gunicorn** (WSGI Server)
- **GitHub Actions** (CI/CD)

## 🛠️ Installation Guide

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Node.js 14+ (for frontend assets)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/copy repo link
   cd rice-mill-management
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file based on `.env.example`:
   ```ini
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=postgres://user:password@localhost:5432/ricemill
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## 🏗️ System Architecture

```
rice-mill-management/
├── core/                      # Main Django app
│   ├── models/                # Database models
│   ├── views/                 # View controllers
│   ├── templates/             # HTML templates
│   └── static/                # Static assets
├── config/                    # Project settings
├── scripts/                   # Utility scripts
├── requirements/              # Dependency files
└── docs/                      # Documentation
```

## 👥 User Roles

1. **Administrator**
   - Full system access
   - User management
   - System configuration

2. **Mill Operator**
   - Paddy processing management
   - Quality control
   - Production reporting

3. **Farmer**
   - Paddy supply tracking
   - Payment history
   - Account management

4. **Customer**
   - Product ordering
   - Order tracking
   - Payment processing

5. **Delivery Personnel**
   - Delivery management
   - Route optimization
   - Status updates

## 📚 API Documentation

The system provides RESTful APIs for integration with mobile apps and third-party services. The API documentation is available in Swagger format at `/api/docs/` when running in development mode.

Key API Endpoints:
- `/api/auth/` - Authentication endpoints
- `/api/paddy/` - Paddy supply management
- `/api/orders/` - Order processing
- `/api/deliveries/` - Delivery tracking

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure your code follows PEP 8 guidelines and includes appropriate tests.

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## ✉️ Contact

Project Maintainer - [Motari](mailto:sammotarih@gmail.com)

Happy coding.

