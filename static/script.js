/**
 * HMS Unified Script: Handles RAG Chat & SQL Appointment Booking
 */

// --- 1. CHAT & RAG SYSTEM ---

async function sendMessage() {
    const input = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const query = input.value.trim();

    if (!query) return;

    // Display User Message
    chatBox.innerHTML += `<div class="message user-message">${query}</div>`;
    input.value = '';
    scrollToBottom();

    // AI Loading State
    const loadingId = "ai-msg-" + Date.now();
    chatBox.innerHTML += `
        <div class="message ai-message" id="${loadingId}">
            <i class="fas fa-spinner fa-spin"></i> Consulting Medical Database...
        </div>`;
    scrollToBottom();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ query: query })
        });
        
        const data = await response.json();
        const aiDiv = document.getElementById(loadingId);
        
        // Format and display the RAG response
        aiDiv.innerHTML = formatMedicalOutput(data.response);
        
    } catch (error) {
        document.getElementById(loadingId).innerHTML = "❌ Error: Could not reach the medical server.";
    }
    scrollToBottom();
}

// --- 2. APPOINTMENT & TRIAGE SYSTEM ---

async function startTriage() {
    const symptomsInput = document.getElementById('symptoms-input');
    const triageResults = document.getElementById('triage-results');
    const symptoms = symptomsInput.value.trim();

    if (!symptoms) {
        alert("Please describe your symptoms first.");
        return;
    }

    triageResults.innerHTML = `
        <div class="col-12 text-center py-4">
            <i class="fas fa-circle-notch fa-spin fa-2x text-primary"></i>
            <p class="mt-2">AI is analyzing symptoms and matching specialists...</p>
        </div>`;

    try {
        const response = await fetch('/get_specialists', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ symptoms: symptoms })
        });
        
        const data = await response.json();
        
        if (data.status === "success" && data.doctors.length > 0) {
            triageResults.innerHTML = ""; // Clear loader
            data.doctors.forEach(doc => {
                triageResults.innerHTML += createDoctorSelectionCard(doc);
            });
        } else {
            triageResults.innerHTML = `
                <div class="alert alert-warning w-100">
                    No matching specialist found for these symptoms. Please visit General OPD.
                </div>`;
        }
    } catch (error) {
        triageResults.innerHTML = `<div class="alert alert-danger w-100">Connection error in triage system.</div>`;
    }
}

// Helper: Create individual doctor card
function createDoctorSelectionCard(doc) {
    return `
        <div class="col-md-6">
            <div class="card h-100 border-primary shadow-sm">
                <div class="card-body">
                    <h5 class="card-title text-primary"><i class="fas fa-user-md"></i> ${doc.name}</h5>
                    <h6 class="card-subtitle mb-2 text-muted">${doc.specialization}</h6>
                    <p class="card-text small">
                        <strong>Shift:</strong> ${doc.time}<br>
                        <strong>Room:</strong> ${doc.room}<br>
                        <strong>Fee:</strong> ${doc.fee}
                    </p>
                    <button class="btn btn-sm btn-primary w-100" onclick="loadSlots(${doc.id}, '${doc.name}')">
                        Select Doctor & View Slots
                    </button>
                    <div id="slots-container-${doc.id}" class="mt-3"></div>
                </div>
            </div>
        </div>`;
}

// Function to fetch and display 20-min slots
async function loadSlots(docId, docName) {
    const container = document.getElementById(`slots-container-${docId}`);
    container.innerHTML = `<small class="text-muted"><i class="fas fa-clock fa-spin"></i> Generating slots...</small>`;

    try {
        const response = await fetch('/get_slots', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ doc_id: docId })
        });
        const data = await response.json();
        
        if (data.status === "success") {
            let slotHtml = `<p class="small mb-1"><strong>Select a time:</strong></p><div class="d-flex flex-wrap gap-1">`;
            data.slots.forEach(slot => {
                slotHtml += `<button class="btn btn-outline-success btn-xs" style="font-size: 0.75rem;" 
                             onclick="confirmBooking('${docName}', '${slot}')">${slot}</button>`;
            });
            slotHtml += `</div>`;
            container.innerHTML = slotHtml;
        }
    } catch (e) {
        container.innerHTML = `<span class="text-danger small">Failed to load slots.</span>`;
    }
}

// Final Booking Step
function confirmBooking(docName, time) {
    const confirmation = confirm(`Confirm appointment with ${docName} at ${time}?`);
    if (confirmation) {
        alert(`✅ Appointment Confirmed!\nDoctor: ${docName}\nTime: ${time}\nPlease arrive 10 minutes early.`);
        // Here you can call /confirm_booking endpoint if needed
    }
}

// --- 3. UTILITIES ---

function formatMedicalOutput(text) {
    if (!text) return "No response generated.";
    return text
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\* (.*?)(?=<br>|$)/g, '• $1');
}

function scrollToBottom() {
    const chatBox = document.getElementById('chat-box');
    if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    if (userInput) {
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }
});