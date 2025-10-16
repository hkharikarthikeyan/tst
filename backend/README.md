# Backend API

Python FastAPI backend with Supabase database for admin panel.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Supabase:**
   - Create a new project at [supabase.com](https://supabase.com)
   - Run the SQL commands from `database_setup.sql` in your Supabase SQL editor
   - Copy your project URL and anon key

3. **Environment variables:**
   Update `.env` file with your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key_here
   SECRET_KEY=your_random_secret_key_here
   ```

4. **Run the server:**
   ```bash
   python run.py
   ```

## API Endpoints

### Admin Authentication
- `POST /signup` - Register new admin user
- `POST /login` - Admin login

### Admin Products Management
- `GET /products` - Get all products
- `POST /products` - Create product (requires admin auth)
- `DELETE /products/{id}` - Delete product (requires admin auth)

### Admin Subscriptions Management
- `GET /subscriptions` - Get all subscriptions
- `POST /subscriptions` - Create subscription (requires admin auth)
- `DELETE /subscriptions/{id}` - Delete subscription (requires admin auth)

### User Authentication
- `POST /user/signup` - Register new customer
- `POST /user/login` - Customer login

### User Products & Subscriptions
- `GET /user/products` - Get all products (customer view)
- `GET /user/subscriptions` - Get all subscription plans
- `POST /user/subscribe` - Subscribe to a plan (requires user auth)
- `GET /user/my-subscriptions` - Get user's active subscriptions

### User Cart Management
- `POST /user/cart/add` - Add item to cart (requires user auth)
- `GET /user/cart` - Get cart items (requires user auth)
- `DELETE /user/cart/{item_id}` - Remove item from cart (requires user auth)

### User Orders
- `POST /user/orders` - Create order from cart (requires user auth)
- `GET /user/orders` - Get user's order history (requires user auth)

## Database Schema

### Admin Users
- id (Primary Key)
- email (Unique)
- password (Hashed)
- created_at

### Customers
- id (Primary Key)
- email (Unique)
- password (Hashed)
- name
- created_at

### Products
- id (Primary Key)
- name
- price
- description
- created_at

### Subscriptions
- id (Primary Key)
- name
- price
- duration
- features (Array)
- created_at

### Customer Subscriptions
- id (Primary Key)
- customer_id (Foreign Key)
- subscription_id (Foreign Key)
- status
- created_at

### Cart Items
- id (Primary Key)
- customer_id (Foreign Key)
- product_id (Foreign Key)
- quantity
- created_at

### Orders
- id (Primary Key)
- customer_id (Foreign Key)
- total_amount
- status
- created_at

### Order Items
- id (Primary Key)
- order_id (Foreign Key)
- product_id (Foreign Key)
- quantity
- created_at