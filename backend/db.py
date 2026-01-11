# backend/db.py
import os
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List

DB_PATH = os.getenv("DB_PATH", os.path.join("backend", "data", "invoices.db"))

def _ensure_folder():
    folder = os.path.dirname(DB_PATH)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

def get_conn():
    _ensure_folder()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        original_filename TEXT,
        stored_path TEXT,
        drive_link TEXT,

        vendor_raw TEXT,
        vendor_norm TEXT,
        date_raw TEXT,
        date_norm TEXT,
        amount_raw TEXT,
        amount_norm TEXT,

        status TEXT NOT NULL,
        error TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_invoice(data: Dict[str, Any]) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO invoices (
        created_at, original_filename, stored_path, drive_link,
        vendor_raw, vendor_norm, date_raw, date_norm, amount_raw, amount_norm,
        status, error
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("created_at") or datetime.utcnow().isoformat(),
        data.get("original_filename"),
        data.get("stored_path"),
        data.get("drive_link"),
        data.get("vendor_raw"),
        data.get("vendor_norm"),
        data.get("date_raw"),
        data.get("date_norm"),
        data.get("amount_raw"),
        data.get("amount_norm"),
        data.get("status", "success"),
        data.get("error"),
    ))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def list_invoices(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM invoices ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
