import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from datetime import datetime

# Internal Project Modules
from src.retriever import MedicalRAGRetriever
from src.ai_engine import MedicalAIEngine
from src.appointment_manager import apt_manager
from src.database_manager import db_manager
from src.embeddings import MedicalEmbeddingManager
from src.vector_store import MedicalVectorManager
from src.logger import logger

load_dotenv()
app = Flask(__name__)

# --- HMS System Initialization ---
try:
    embed_manager = MedicalEmbeddingManager()
    embeddings = embed_manager.get_embeddings()
    vstore_manager = MedicalVectorManager(embedding_model=embeddings)
    vectorstore = vstore_manager.get_vectorstore_object()
    retriever = MedicalRAGRetriever(vectorstore)
    ai_brain = MedicalAIEngine()
    logger.info("✅ HMS Systems Online.")
except Exception as e:
    logger.critical(f"❌ Boot Failure: {str(e)}")

# --- UI ROUTES ---

@app.route('/')
def dashboard_page():
    # Database se real counts lena
    db_manager.cursor.execute("SELECT COUNT(*) FROM appointments")
    total_apt = db_manager.cursor.fetchone()[0]
    
    db_manager.cursor.execute("SELECT COUNT(*) FROM doctors")
    total_doc = db_manager.cursor.fetchone()[0]
    
    # AI Queries count (Yahan 150 ki jagah 0 rakhein agar table nahi hai)
    ai_count = 150 
    
    return render_template('dashboard.html', total_apt=total_apt, total_doc=total_doc, ai_count=ai_count)

# Naya Route: Doctors ki details dekhne ke liye
@app.route('/admin/doctors')
def view_doctors():
    try:
        # Hum sirf Name aur Specialization select kar rahe hain
        db_manager.cursor.execute("SELECT name, specialization FROM doctors")
        doctors_list = db_manager.cursor.fetchall()
        return render_template('view_doctors.html', doctors=doctors_list)
    except Exception as e:
        return f"Database Error: {str(e)}"

# Appointments list dikhane ka function
# Inside app.py
@app.route('/admin/all-appointments')
def view_all_appointments():
    query = """
        SELECT a.id, a.patient_name, d.name, a.appointment_date, a.time_slot, 
               a.email, a.whatsapp, a.arrival_status, a.arrival_time 
        FROM appointments a 
        LEFT JOIN doctors d ON a.doctor_id = d.id
    """
    db_manager.cursor.execute(query)
    rows = db_manager.cursor.fetchall()
    
    appointments_list = []
    for r in rows:
        appointments_list.append({
            "id": r[0], "patient": r[1], "doctor": r[2], "date": r[3], 
            "time": r[4], "email": r[5], "whatsapp": r[6],
            "arrival_status": r[7], "arrival_time": r[8] # Added these
        })
    return render_template('all_appointments_detail.html', appointments=appointments_list)
    
# Delete karne ka function
@app.route('/delete-appointment/<int:id>')
def delete_appointment(id):
    try:
        db_manager.cursor.execute("DELETE FROM appointments WHERE id = ?", (id,))
        db_manager.conn.commit()
        return redirect(url_for('view_all_appointments'))
    except Exception as e:
        return f"Delete Error: {e}"
    
@app.route('/ai-assistant')
def chat_page():
    return render_template('chat.html')

@app.route('/appointments')
def appointment_view():
    return render_template('appointment.html')

# @app.route('/admin')
# def admin_dashboard():
#     """Admin View to see all bookings"""
#     return render_template('admin_dashboard.html')

# --- API ENDPOINTS ---

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_query = data.get('query', '').strip()
        if not user_query:
            return jsonify({"response": "I am ready to assist. Please enter your query."})

        context_docs = retriever.retrieve(user_query, top_k=3)
        answer = ai_brain.generate_response(user_query, context_docs)
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"response": "Service temporarily unavailable."})

@app.route('/get_specialists', methods=['POST'])
def get_specialists():
    try:
        data = request.json
        symptoms = data.get('symptoms', '').strip()
        doctors_list_all = db_manager.get_all_doctors_minimal()
        
        ai_suggestion = ai_brain.recommend_doctor(symptoms, doctors_list_all)
        
        # 1. Match by Specialization
        matched_doctors = apt_manager.get_doctors_by_specialty(ai_suggestion)
        
        # 2. Fallback to Name Search
        if not matched_doctors:
            query = "SELECT id, name, specialization, start_time, end_time, room, fee FROM doctors WHERE name LIKE ?"
            db_manager.cursor.execute(query, (f"%{ai_suggestion.replace('Dr. ', '')}%",))
            matched_doctors = db_manager.cursor.fetchall()

        # 3. Emergency Fallback
        if not matched_doctors:
            db_manager.cursor.execute("SELECT id, name, specialization, start_time, end_time, room, fee FROM doctors LIMIT 3")
            matched_doctors = db_manager.cursor.fetchall()

        doctor_data = [{
            "id": doc[0], "name": doc[1], "specialization": doc[2],
            "time": f"{doc[3]} - {doc[4]}", "room": doc[5], "fee": doc[6]
        } for doc in matched_doctors]
        
        return jsonify({"status": "success", "doctors": doctor_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/get_all_doctors', methods=['GET'])
def get_all_doctors():
    """Route for the second tab 'All Specialists'"""
    try:
        db_manager.cursor.execute("SELECT id, name, specialization, start_time, end_time, room, fee FROM doctors")
        all_docs = db_manager.cursor.fetchall()
        doctor_data = [{
            "id": doc[0], "name": doc[1], "specialization": doc[2],
            "time": f"{doc[3]} - {doc[4]}", "room": doc[5], "fee": doc[6]
        } for doc in all_docs]
        return jsonify({"status": "success", "doctors": doctor_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/get_slots', methods=['POST'])
def get_slots():
    data = request.json
    doc_id = data.get('doc_id')
    apt_date = data.get('date') # Frontend se aane wali date
    
    # Doctor ki full timing DB se lein
    db_manager.cursor.execute("SELECT start_time, end_time FROM doctors WHERE id=?", (doc_id,))
    res = db_manager.cursor.fetchone()
    
    if res:
        all_slots = apt_manager.generate_time_slots(res[0], res[1])
        
        # Check karein ke is date par kitne slots booked hain
        db_manager.cursor.execute(
            "SELECT time_slot FROM appointments WHERE doctor_id=? AND appointment_date=? AND status='Confirmed'",
            (doc_id, apt_date)
        )
        booked_slots = [row[0] for row in db_manager.cursor.fetchall()]
        
        # Available aur booked ki list banayein
        slot_data = [{"time": s, "is_booked": s in booked_slots} for s in all_slots]
        return jsonify({"status": "success", "slots": slot_data})
        
    return jsonify({"status": "error", "message": "Doctor timings not found."})

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    """Saves appointment with Email and WhatsApp to database"""
    try:
        data = request.json
        # Check karein ke frontend se email aur whatsapp aa raha hai
        p_email = data.get('email')
        p_whatsapp = data.get('whatsapp')

        query = """
            INSERT INTO appointments (patient_name, doctor_id, appointment_date, time_slot, email, whatsapp, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Confirmed')
        """
        db_manager.cursor.execute(query, (
            data.get('patient'),
            data.get('doc_id'),
            data.get('date'),
            data.get('time'),
            p_email,     # Naya column
            p_whatsapp   # Naya column
        ))
        db_manager.conn.commit()
        
        logger.info(f"✅ Booked: {data.get('patient')} | Email: {p_email} | WA: {p_whatsapp}")
        return jsonify({"status": "success", "message": "Appointment confirmed!"})
    except Exception as e:
        logger.error(f"Booking Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/get_all_appointments', methods=['GET'])
def get_all_appointments():
    """API for Admin Dashboard table including Email and WhatsApp"""
    try:
        # Humne SELECT query mein email aur whatsapp ko shamil kar liya hai
        query = """
            SELECT a.id, a.patient_name, d.name, a.appointment_date, a.time_slot, a.status, a.email, a.whatsapp 
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            ORDER BY a.appointment_date DESC
        """
        db_manager.cursor.execute(query)
        rows = db_manager.cursor.fetchall()
        
        # Dictionary mein mapping update kar di
        appts = [{
            # "id": r[0], 
            "patient": r[1], 
            "doctor": r[2],
            "date": r[3], 
            "time": r[4], 
            "status": r[5],
            "email": r[6] if r[6] else "N/A",      # Email handle
            "whatsapp": r[7] if r[7] else "N/A"    # WhatsApp handle
        } for r in rows]
        
        return jsonify({"status": "success", "appointments": appts})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    

@app.route('/check-in/<int:appointment_id>')
def check_in_patient(appointment_id):
    """
    Triggered when a patient scans the QR code at the hospital.
    Updates status to 'Arrived' so the Doctor knows they are ready.
    """
    try:
        current_time = datetime.now().strftime("%I:%M %p")
        
        # Update arrival status in database
        query = """
            UPDATE appointments 
            SET arrival_status = 'Arrived', arrival_time = ? 
            WHERE id = ?
        """
        db_manager.cursor.execute(query, (current_time, appointment_id))
        db_manager.conn.commit()
        
        # Logic for Automation: You can trigger an n8n webhook here 
        # to notify the doctor's screen immediately.
        
        return f"""
            <div style='text-align:center; padding:50px; font-family:sans-serif;'>
                <h1 style='color:#28a745;'>Check-in Successful!</h1>
                <p>Arrival Time: {current_time}</p>
                <p>Please take a seat. The doctor has been notified.</p>
            </div>
        """
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    

@app.route('/reception-qr')
def reception_gateway():
    """Main page opened by the counter QR code"""
    return render_template('reception_gateway.html')

@app.route('/process-checkin', methods=['POST'])
def process_checkin():
    """Handles existing appointment check-ins via ID"""
    try:
        apt_id = request.form.get('appointment_id')
        current_time = datetime.now().strftime("%I:%M %p")
        
        # Verify if ID exists
        db_manager.cursor.execute("SELECT id FROM appointments WHERE id = ?", (apt_id,))
        if not db_manager.cursor.fetchone():
            return "<h3>Error: Appointment ID not found. Please ask the receptionist.</h3>"

        # Update status
        db_manager.cursor.execute("""
            UPDATE appointments SET arrival_status = 'Arrived', arrival_time = ? 
            WHERE id = ?
        """, (current_time, apt_id))
        db_manager.conn.commit()
        
        return f"<h3>Welcome! Your attendance is marked at {current_time}. Please wait.</h3>"
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(debug=True, port=5000)