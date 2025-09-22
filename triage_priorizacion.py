"""
Script de priorización y manejo de llamadas de emergencia para triage automático.
Cumple las reglas de seguridad y lógica de priorización descritas.
"""
import uuid
from datetime import datetime

# Palabras clave críticas
CRITICAL_KEYWORDS = ["no respira", "atrapado", "incendio activo", "persona inconsciente"]

# Severidad y prioridad
SEVERITY_HIGH = "alta"
SEVERITY_MEDIUM = "media"
SEVERITY_LOW = "baja"

STATUS_ENROUTED = "enrouted"
STATUS_ENQUEUED = "enqueued"
STATUS_DISPATCHED = "dispatched"
STATUS_CLOSED = "closed"

# Operadores simulados
OPERATORS = [
    {"id": "op1", "name": "Juan", "status": "available", "current_case_id": None},
    {"id": "op2", "name": "Ana", "status": "busy", "current_case_id": "20250918-000123"},
]

def calculate_priority_score(entities, intent, confidence, transcription, time_in_queue=0):
    score = 0
    # Palabras críticas
    for kw in CRITICAL_KEYWORDS:
        if kw in transcription.lower():
            score += 50
    # Heridos
    score += 20 * entities.get("num_injured", 0)
    # Accidente/colapso
    if intent in ["traffic_accident", "collapse"]:
        score += 25
    # Confianza baja
    if confidence < 0.7:
        score -= 10
    # Tiempo en cola
    if time_in_queue > 180:
        score += 10
    return score

def classify_severity(transcription, entities):
    for kw in CRITICAL_KEYWORDS:
        if kw in transcription.lower():
            return SEVERITY_HIGH
    if entities.get("person_unconscious") or entities.get("fire_active"):
        return SEVERITY_HIGH
    if entities.get("num_injured", 0) > 0:
        return SEVERITY_MEDIUM
    return SEVERITY_LOW

def assign_operator():
    for op in OPERATORS:
        if op["status"] == "available":
            return op
    return None

def handle_call(caller_number, transcription, entities, intent, confidence, audio_recording_id, time_in_queue=0):
    severity = classify_severity(transcription, entities)
    priority_score = calculate_priority_score(entities, intent, confidence, transcription, time_in_queue)
    case_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:6]}"
    timestamp = datetime.now().isoformat()
    status = STATUS_ENROUTED if severity == SEVERITY_HIGH else STATUS_ENQUEUED
    operator = assign_operator()

    # Regla: nunca cortar si severity alta
    if severity == SEVERITY_HIGH:
        if operator:
            status = STATUS_DISPATCHED
            operator["status"] = "busy"
            operator["current_case_id"] = case_id
            message = "Transferencia inmediata a operador. Mantenga la llamada, ayuda en camino."
        else:
            message = "Todos los operadores ocupados. Mantenga la llamada, ayuda en camino."
    else:
        if operator:
            status = STATUS_DISPATCHED
            operator["status"] = "busy"
            operator["current_case_id"] = case_id
            message = "Transferencia a operador humano."
        else:
            status = STATUS_ENQUEUED
            message = f"Recibimos tu aviso como caso {case_id} con prioridad {severity}. Todos los operadores ocupados. Se ha despachado asistencia. Si la situación empeora, llamá de nuevo o marcá 0 para intentar hablar con un operador. Gracias."

    # Construir JSON de salida
    case_json = {
        "case_id": case_id,
        "timestamp": timestamp,
        "caller_number": caller_number,
        "transcription": transcription,
        "intent": intent,
        "entities": entities,
        "severity": severity,
        "priority_score": priority_score,
        "confidence": confidence,
        "audio_recording_id": audio_recording_id,
        "status": status
    }
    return case_json, message

# Ejemplo de uso
def main():
    caller_number = "+5492611234567"
    transcription = "Chocamos en la ruta 188, hay dos personas lastimadas, una no está consciente, vení rápido"
    entities = {"location": "Ruta 188 km 45", "num_injured": 2, "person_unconscious": True}
    intent = "traffic_accident"
    confidence = 0.95
    audio_recording_id = "audio_abc123"
    case_json, message = handle_call(caller_number, transcription, entities, intent, confidence, audio_recording_id)
    print("JSON generado:")
    print(case_json)
    print("Mensaje al llamante:")
    print(message)

if __name__ == "__main__":
    main()
