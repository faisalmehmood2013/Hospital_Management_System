import sqlite3
import os

def check_database_structure():
    # 1. Database file ka naam check karein
    # Agar aapki file ka naam 'hospital.db' ke ilawa kuch aur hai to yahan change karein
    db_name = 'hospital_management.db'
    
    if not os.path.exists(db_name):
        print(f"Error: Database file '{db_name}' nahi mili! Please sahi naam check karein.")
        return

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Un tables ki list jinhein humne check karna hai
        tables = ['appointments', 'doctors']
        
        print("="*50)
        print("DATABASE STRUCTURE REPORT")
        print("="*50)

        for table in tables:
            print(f"\n[Table: {table.upper()}]")
            print("-" * 30)
            
            # PRAGMA table_info se columns ki details milti hain
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            if not columns:
                print(f"Bhai, '{table}' naam ka koi table nahi mila database mein.")
            else:
                print(f"{'ID':<5} | {'Column Name':<20} | {'Type':<10}")
                print("-" * 35)
                for col in columns:
                    # col[0]=cid, col[1]=name, col[2]=type
                    print(f"{col[0]:<5} | {col[1]:<20} | {col[2]:<10}")
        
        print("\n" + "="*50)
        print("Column Name.")
        print("="*50)

    except Exception as e:
        print(f"Kuch ghalat ho gaya: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_database_structure()