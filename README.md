# RMAD System 🏭🌾

**RMAD (Rice Milling and Distribution) System** is a comprehensive web-based application for managing the end-to-end process of rice distribution, including farmer supply, inventory tracking, rice processing, order handling, and delivery.

---

## 🚀 Features

- **User Roles & Authentication**
  - **Admins**: Manage the system, users, and approve payments
  - **Mill Operators**: Process paddy into rice
  - **Farmers**: Supply paddy and track payments
  - **Customers**: Place rice orders
  - **Delivery Personnel**: Handle customer deliveries

- **Inventory Management**
  - Track unprocessed paddy, processed rice, and packed rice
  - Automatic updates on supply and processing

- **Order & Cart System**
  - Customers can add/subtract package sizes using interactive icons
  - Auto-calculated totals
  - Inventory deducted upon ordering

- **Farmer Payment Management**
  - Total supplied paddy tracked
  - Admin can view and approve payments

- **Admin Dashboard**
  - Add/manage users by role
  - View statistics and approve transactions

---

## 🛠 Tech Stack

- **Backend**: Django 5+
- **Frontend**: Django Templates, Bootstrap
- **Database**: SQLite (default) / PostgreSQL (recommended)
- **Others**: HTML, CSS, JavaScript

---

## 📦 Installation

1. **Clone the Repo**

```bash
git clone [https://github.com/sammotari/rmad_system.git](https://github.com/sammotari/rice_milling_and_distribution.git)
cd rmad_system

    Create Virtual Environment & Install Requirements

python -m venv venv
# On Windows use venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt

    Run Migrations

python manage.py makemigrations
python manage.py migrate

    Create Superuser

python manage.py createsuperuser
python manage.py populate

    Run the Server

python manage.py runserver

🔐 User Roles
Role	Permissions
Admin	Full access, add users, approve payments
Mill Operator	Add/process rice, update inventories
Farmer	View own supplies and payment status
Customer	Place orders
Delivery	View assigned deliveries
📄 License

This project is licensed under the MIT License.
✨ Author

Samwel Motari
💼 MOTARI CORP
📷 Dream Lens Studio
📧 sammotari@gmail.com
📌 Contribution

Contributions are welcome! Feel free to fork the repo and submit a PR.
