import sqlite3

def add_missing_columns():
    db_path = 'hospital_management.db' # Check karein aapki db file ka sahi naam
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Email column add karne ke liye
        cursor.execute("ALTER TABLE appointments ADD COLUMN email TEXT")
        print("Email column added successfully!")
    except sqlite3.OperationalError:
        print("Email column pehle se mojood hai.")

    try:
        # Whatsapp column add karne ke liye
        cursor.execute("ALTER TABLE appointments ADD COLUMN whatsapp TEXT")
        print("Whatsapp column added successfully!")
    except sqlite3.OperationalError:
        print("Whatsapp column pehle se mojood hai.")

    conn.commit()
    conn.close()
    print("Database Update Complete!")

def update_db_schema():
    db_path = 'hospital_management.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Add arrival_status to track if patient is 'Pending', 'Arrived', or 'In-Consultation'
        cursor.execute("ALTER TABLE appointments ADD COLUMN arrival_status TEXT DEFAULT 'Pending'")
        
        # Add arrival_time to log exactly when they scanned the QR code
        cursor.execute("ALTER TABLE appointments ADD COLUMN arrival_time TEXT")
        
        conn.commit()
        print("✅ Database schema updated successfully!")
    except Exception as e:
        print(f"⚠️ Column update note: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_missing_columns()
    update_db_schema()