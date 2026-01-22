import sqlite3
from src.logger import logger

class HospitalDB:
    def __init__(self, db_path="hospital_management.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        """Creates doctors and appointments tables if they do not exist."""
        try:
            # Doctors Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    specialization TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    room TEXT,
                    fee TEXT
                )
            ''')
            
            # Appointments Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_name TEXT,
                    doctor_id INTEGER,
                    appointment_date TEXT,
                    time_slot TEXT,
                    status TEXT DEFAULT 'Confirmed',
                    FOREIGN KEY(doctor_id) REFERENCES doctors(id)
                )
            ''')
            self.conn.commit()
            logger.info("Database tables initialized successfully.")
        except Exception as e:
            logger.error(f"Database setup error: {e}")

    def add_doctor(self, name, spec, start, end, room, fee):
        """Inserts a new doctor record into the database."""
        self.cursor.execute('''
            INSERT INTO doctors (name, specialization, start_time, end_time, room, fee)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, spec, start, end, room, fee))
        self.conn.commit()

    def get_all_doctors_minimal(self):
        """Returns a list of doctors and their specialties for the AI to analyze."""
        self.cursor.execute("SELECT name, specialization FROM doctors")
        return self.cursor.fetchall()

    def get_doctor_details_by_name(self, doctor_name):
        """Fetches full doctor details by name using flexible matching."""
        query = "SELECT * FROM doctors WHERE name LIKE ?"
        self.cursor.execute(query, (f"%{doctor_name}%",))
        return self.cursor.fetchone()

# Global instance
db_manager = HospitalDB()