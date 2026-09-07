"""This file will:

Create a SQLite database file called ecommerce.db
Create all 12 tables
Insert sample data"""

# Chunk 1 - connect and create the first two tables:

import sqlite3

# creates ecommerce.db file if it does not exist and connects if it does exist
conn = sqlite3.connect("ecommerce.db")
cursor = conn.cursor()

# conn -> opens the connection
# cursor -> executes queries and fetches results

"""cursor.execute("SQL here") — sends a query to the database
cursor.fetchall() — retrieves all results from the last query
conn.commit() — saves any changes permanently (like pressing "save" — without this, inserts and updates don't actually stick)"""


"""AUTOINCREMENT — yes, it's a serial number that auto-assigns the next integer every time a new row is inserted. You never have to manually provide a customer_id — SQLite handles it automatically. 1, 2, 3... and so on."""
# create categories table
cursor.execute("""
               CREATE TABLE IF NOT EXISTS categories (
               category_id INTEGER PRIMARY KEY AUTOINCREMENT,
               category_name TEXT NOT NULL
               )
               """)

# create customers table
cursor.execute("""
               CREATE TABLE IF NOT EXISTS customers (
               customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               email TEXT UNIQUE NOT NULL,
               phone TEXT,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
               )
               """)
cursor.execute("""
               CREATE TABLE IF NOT EXISTS products (
               product_id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT NOT NULL,
               description TEXT,
               price REAL NOT NULL,
               stock_quantity INTEGER DEFAULT 0,
               category_id INTEGER,
               FOREIGN KEY (category_id) REFERENCES categories(category_id)
               )
               """)
cursor.execute("""
               CREATE TABLE IF NOT EXISTS sellers (
               seller_id INTEGER PRIMARY KEY AUTOINCREMENT,
               store_name TEXT NOT NULL,
               email TEXT UNIQUE NOT NULL,
               phone TEXT,
               ships_from TEXT,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
               )
               """)
cursor.execute("""
               CREATE TABLE IF NOT EXISTS orders (
               order_id INTEGER PRIMARY KEY AUTOINCREMENT,
               customer_id INTEGER,
               status TEXT DEFAULT 'pending',
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
               )
               """)
cursor.execute("""
               CREATE TABLE IF NOT EXISTS order_items (
               order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
               order_id INTEGER,
               product_id INTEGER,
               quantity INTEGER NOT NULL,
               price_at_time REAL NOT NULL,
               FOREIGN KEY (order_id) REFERENCES orders(order_id),
               FOREIGN KEY (product_id) REFERENCES products(product_id)
               )
               """)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart_items (
        cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        quantity INTEGER NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        review_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        order_id INTEGER,
        amount REAL NOT NULL,
        payment_method TEXT,
        transaction_status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS returns (
        return_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        order_item_id INTEGER,
        refund_account TEXT,
        scheduled_date DATE,
        return_status TEXT DEFAULT 'requested',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (order_item_id) REFERENCES order_items(order_item_id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS addresses (
        address_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        label TEXT,
        street TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_sellers (
        product_seller_id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id INTEGER,
        product_id INTEGER,
        seller_price REAL NOT NULL,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (seller_id) REFERENCES sellers(seller_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
""")

conn.commit()
print("All tables created.")

"""Exactly right — but there's one more layer worth knowing. It's not just connecting them logically — FOREIGN KEY enforces referential integrity.
Meaning: if you try to insert a review with customer_id = 999 but no customer with ID 999 exists in the customers table, the database will reject that insert. It prevents orphaned data — reviews without real customers, order items without real orders, and so on.
It's the database itself acting as a safety net, not just your application code."""

# Chunk 3 - Inserting sample data

# categories

cursor.executemany("INSERT INTO categories (category_name) VALUES (?)", [
    ("Electronics",),
    ("Clothing",),
    ("Books",),
    ("Sports",),
    ("Home & Kitchen",),
])

# Customers

cursor.executemany("INSERT INTO customers (name,email,phone) VALUES (?, ?, ?)", [
    ("Amit Sharma",    "amit@gmail.com",   "9876543210"),
    ("Priya Patel",    "priya@gmail.com",  "9876543211"),
    ("Rohan Verma",    "rohan@gmail.com",  "9876543212"),
    ("Sneha Iyer",     "sneha@gmail.com",  "9876543213"),
    ("Karan Mehta",    "karan@gmail.com",  "9876543214"),
])


# products
cursor.executemany(
    "INSERT INTO products (title, description, price, stock_quantity, category_id) VALUES (?, ?, ?, ?, ?)", [
    ("Football",         "Official size football",         499.0,  50, 4),
    ("Cricket Bat",      "Willow cricket bat",             1299.0, 30, 4),
    ("Python Book",      "Learn Python programming",       599.0,  100,3),
    ("Running Shoes",    "Lightweight running shoes",      1999.0, 40, 2),
    ("Wireless Earbuds", "Bluetooth 5.0 earbuds",         2499.0, 60, 1),
    ("Yoga Mat",         "Non-slip yoga mat",              799.0,  45, 4),
    ("Cooking Pan",      "Non-stick frying pan",           999.0,  35, 5),
    ("T-Shirt",          "Cotton round neck t-shirt",      399.0,  80, 2),
])

# sellers
cursor.executemany(
    "INSERT INTO sellers (store_name, email, phone, ships_from) VALUES (?, ?, ?, ?)", [
    ("SportZone",      "sport@zone.com",   "9111111111", "Mumbai"),
    ("BookWorld",      "book@world.com",   "9222222222", "Delhi"),
    ("TechMart",       "tech@mart.com",    "9333333333", "Bangalore"),
    ("FashionHub",     "fashion@hub.com",  "9444444444", "Chennai"),
])

# product_sellers
cursor.executemany(
    "INSERT INTO product_sellers (seller_id, product_id, seller_price) VALUES (?, ?, ?)", [
    (1, 1, 479.0),
    (1, 2, 1249.0),
    (2, 3, 579.0),
    (3, 5, 2399.0),
    (4, 4, 1899.0),
    (4, 8, 379.0),
])

# orders
cursor.executemany(
    "INSERT INTO orders (customer_id, status) VALUES (?, ?)", [
    (1, "delivered"),
    (2, "in transit"),
    (3, "pending"),
    (1, "delivered"),
    (4, "in transit"),
    (5, "pending"),
    (2, "delivered"),
    (3, "in transit"),
])

# order_items
cursor.executemany(
    "INSERT INTO order_items (order_id, product_id, quantity, price_at_time) VALUES (?, ?, ?, ?)", [
    (1, 1, 2, 499.0),
    (1, 3, 1, 599.0),
    (2, 5, 1, 2499.0),
    (3, 2, 1, 1299.0),
    (4, 4, 1, 1999.0),
    (5, 6, 2, 799.0),
    (6, 7, 1, 999.0),
    (7, 8, 3, 399.0),
    (8, 1, 1, 499.0),
])

# cart_items
cursor.executemany(
    "INSERT INTO cart_items (customer_id, product_id, quantity) VALUES (?, ?, ?)", [
    (1, 5, 1),
    (2, 6, 2),
    (3, 8, 1),
    (4, 3, 1),
])

# reviews
cursor.executemany(
    "INSERT INTO reviews (customer_id, product_id, rating, review_text) VALUES (?, ?, ?, ?)", [
    (1, 1, 5, "Great football, very durable!"),
    (1, 3, 4, "Good book for beginners."),
    (2, 5, 5, "Excellent sound quality!"),
    (3, 2, 3, "Decent bat but slightly heavy."),
    (4, 6, 4, "Good yoga mat, non-slip works well."),
    (5, 7, 5, "Perfect non-stick pan!"),
])

# payments
cursor.executemany(
    "INSERT INTO payments (customer_id, order_id, amount, payment_method, transaction_status) VALUES (?, ?, ?, ?, ?)", [
    (1, 1, 1597.0, "UPI",        "success"),
    (2, 2, 2499.0, "Credit Card","success"),
    (3, 3, 1299.0, "UPI",        "pending"),
    (1, 4, 1999.0, "Debit Card", "success"),
    (4, 5, 1598.0, "UPI",        "success"),
    (5, 6, 999.0,  "COD",        "pending"),
    (2, 7, 1197.0, "Credit Card","success"),
    (3, 8, 499.0,  "UPI",        "success"),
])

# returns
cursor.executemany(
    "INSERT INTO returns (customer_id, order_item_id, refund_account, scheduled_date, return_status) VALUES (?, ?, ?, ?, ?)", [
    (3, 3, "rohan@upi",  "2025-05-10", "approved"),
    (5, 7, "karan@upi",  "2025-05-12", "requested"),
])

# addresses
cursor.executemany(
    "INSERT INTO addresses (customer_id, label, street, city, state, zip_code) VALUES (?, ?, ?, ?, ?, ?)", [
    (1, "home", "12 MG Road",     "Mumbai",    "Maharashtra", "400001"),
    (2, "home", "45 Park Street", "Delhi",     "Delhi",       "110001"),
    (3, "work", "7 Tech Park",    "Bangalore", "Karnataka",   "560001"),
    (4, "home", "22 Anna Nagar",  "Chennai",   "Tamil Nadu",  "600001"),
    (5, "home", "8 Civil Lines",  "Lucknow",   "UP",          "226001"),
])

conn.commit()
conn.close()
print("Sample data inserted successfully.")