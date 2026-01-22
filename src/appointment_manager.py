from src.database_manager import db_manager
from src.ai_engine import MedicalAIEngine
from src.logger import logger
from datetime import datetime, timedelta

class AppointmentManager:
    def __init__(self):
        self.ai_engine = MedicalAIEngine()

    def get_specialists_by_query(self, symptoms: str):
        """
        AI identifies the specialty, then SQL fetches all matching doctors.
        This fixes the 'No specialist found' error by broadening the search.
        """
        try:
            # 1. Get minimal list for AI context
            doctors_data = db_manager.get_all_doctors_minimal()
            
            # 2. AI identifies the specialization needed
            # (e.g., Returns 'Cardiologist' instead of just one name)
            recommendation = self.ai_engine.recommend_doctor(symptoms, doctors_data)
            logger.info(f"AI triage result: {recommendation}")

            # 3. Flexible search: Try matching by Specialization FIRST
            matched_doctors = self.get_doctors_by_specialty(recommendation)
            
            # 4. Fallback: If no specialty match, try matching by Doctor Name
            if not matched_doctors:
                clean_name = recommendation.replace("Dr.", "").replace("Prof.", "").strip()
                query = "SELECT * FROM doctors WHERE name LIKE ?"
                db_manager.cursor.execute(query, (f"%{clean_name}%",))
                matched_doctors = db_manager.cursor.fetchall()

            return matched_doctors
            
        except Exception as e:
            logger.error(f"Triage logic failure: {e}")
            return []

    def get_doctors_by_specialty(self, specialization: str):
        """Fetches all doctors from SQL based on specialization."""
        try:
            query = "SELECT * FROM doctors WHERE specialization LIKE ?"
            db_manager.cursor.execute(query, (f"%{specialization}%",))
            return db_manager.cursor.fetchall()
        except Exception as e:
            logger.error(f"Database specialty search error: {e}")
            return []

    def generate_time_slots(self, start_str, end_str):
        """Divides working hours into professional 20-min booking intervals."""
        slots = []
        # Support for common time formats
        time_format = "%I:%M %p" 
        try:
            start_dt = datetime.strptime(start_str.strip(), time_format)
            end_dt = datetime.strptime(end_str.strip(), time_format)
            
            current = start_dt
            while current + timedelta(minutes=20) <= end_dt:
                slots.append(current.strftime(time_format))
                current += timedelta(minutes=20)
        except Exception as e:
            logger.error(f"Slot Generation Error for {start_str}-{end_str}: {e}")
        return slots

    def get_ai_recommendation(self, symptoms: str):
        """Single doctor recommendation logic (Old version maintained for compatibility)."""
        try:
            doctors_data = db_manager.get_all_doctors_minimal()
            recommended_name = self.ai_engine.recommend_doctor(symptoms, doctors_data)
            
            clean_name = recommended_name.replace("Dr.", "").replace("Prof.", "").strip()
            doc_details = db_manager.get_doctor_details_by_name(clean_name)

            if doc_details:
                return {
                    "status": "success",
                    "doctor_name": doc_details[1],
                    "specialization": doc_details[2],
                    "time": f"{doc_details[3]} - {doc_details[4]}",
                    "room": doc_details[5],
                    "fee": doc_details[6]
                }
            return {"status": "error", "message": "Specialist not found in schedule."}
        except Exception as e:
            logger.error(f"Recommendation Error: {e}")
            return {"status": "error", "message": "System triage failed."}

apt_manager = AppointmentManager()