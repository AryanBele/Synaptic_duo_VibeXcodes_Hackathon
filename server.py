"""
Bol-Khata (बोल-खाता) — Backend Server (FastAPI / SQLite Option)
VibeX Codes Hackathon — Track 1 Submission
"""

import sqlite3
import json
from datetime import datetime

DATABASE_NAME = "bol_khata.db"

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Customers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        phone TEXT,
        balance REAL DEFAULT 0.0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # Transactions / Audit Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        raw_speech TEXT,
        items TEXT,
        amount REAL NOT NULL,
        txn_type TEXT NOT NULL, -- 'credit' or 'payment'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()
    print("SQLite Database initialized: bol_khata.db")

def add_transaction(customer_name, amount, txn_type, raw_speech="", items=""):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Ensure customer exists
    cursor.execute("INSERT OR IGNORE INTO customers (name, balance) VALUES (?, 0)", (customer_name,))
    
    # Update balance
    if txn_type == 'credit':
        cursor.execute("UPDATE customers SET balance = balance + ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?", (amount, customer_name))
    else:
        cursor.execute("UPDATE customers SET balance = MAX(0, balance - ?), updated_at = CURRENT_TIMESTAMP WHERE name = ?", (amount, customer_name))
        
    # Log transaction
    cursor.execute("""
    INSERT INTO transactions (customer_name, raw_speech, items, amount, txn_type)
    VALUES (?, ?, ?, ?, ?)
    """, (customer_name, raw_speech, items, amount, txn_type))
    
    conn.commit()
    conn.close()
    return {"status": "success", "customer": customer_name, "amount": amount, "type": txn_type}

def get_ledger_summary():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, balance FROM customers WHERE balance > 0 ORDER BY balance DESC")
    debts = cursor.fetchall()
    conn.close()
    return [{"customer": row[0], "balance": row[1]} for row in debts]

if __name__ == "__main__":
    init_db()
    # Sample Test
    add_transaction("Ramesh", 35.0, "credit", "Ramesh 2 chai 1 bun maska", "2 Chai, 1 Bun Maska")
    add_transaction("Suresh", 50.0, "credit", "Suresh ko 50 rupaye udhaar", "Direct Udhaar")
    print("Current Outstanding Khata:")
    print(json.dumps(get_ledger_summary(), indent=2))
