import csv
import os
from src.database_manager import db_manager
from src.logger import logger

def sync_csv_to_sql(file_path):
    """Reads doctor data from CSV and populates the SQL database."""
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found!")
        return

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Clear existing data to avoid duplicates (Optional)
            db_manager.cursor.execute("DELETE FROM doctors")
            
            count = 0
            for row in reader:
                db_manager.add_doctor(
                    name=row['Doctor Name'],
                    spec=row['Specialization'],
                    start=row['Available Time'].split('-')[0].strip(),
                    end=row['Available Time'].split('-')[1].strip(),
                    room=row['Room No'],
                    fee=row['Fee']
                )
                count += 1
            
            logger.info(f"Successfully synced {count} doctors to the database.")
            print(f"✅ Success: {count} doctors imported to SQL database.")

    except Exception as e:
        logger.error(f"Sync Error: {str(e)}")
        print(f"❌ Sync Failed: {e}")

if __name__ == "__main__":
    # Ensure your file name matches here
    sync_csv_to_sql("doctors_data.csv")