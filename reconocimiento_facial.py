import cv2
from deepface import DeepFace
import numpy as np
from scipy.spatial.distance import cosine
import requests
from datetime import datetime

# Configuración de la URL de Magic Loops
magicloops_url = "https://magicloops.dev/api/loop/run/4104dda6-72f6-452c-a4af-f5b32d8cd0e6"

# Diccionario para registrar la última fecha en que se envió la solicitud para cada persona
last_sent_date = {}

# Función para enviar la solicitud a Magic Loops
def send_to_magicloops(recognized_name, min_distance):
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    input_text = f"Se ha detectado a {recognized_name} con una distancia de {min_distance:.2f}. Fecha y hora: {date_time}"
    
    params = {
        "input": input_text
    }

    response = requests.get(magicloops_url, params=params)

    if response.status_code == 200:
        print("Webhook activado con éxito en Magic Loops.")
    else:
        print("Error al activar el webhook:", response.status_code)

# Función para verificar si ya se envió una solicitud hoy para una persona
def should_send_notification(name):
    today_date = datetime.now().date()
    if name in last_sent_date:
        if last_sent_date[name] == today_date:
            return False  # Ya se envió la solicitud hoy
    last_sent_date[name] = today_date  # Actualiza la fecha de envío a hoy
    return True

# Configuración de la base de datos con imágenes de referencia
database = {}
reference_images = {
    "joaquin": [
        "imagen1.jpg",
        "imagen2.jpg"
    ]
}

# Generar embeddings para cada imagen y guardarlos en la base de datos
for name, img_paths in reference_images.items():
    embeddings = []
    for img_path in img_paths:
        embedding = DeepFace.represent(img_path=img_path, model_name="Facenet", enforce_detection=False)[0]["embedding"]
        embeddings.append(embedding)
    database[name] = embeddings

# Función para encontrar la persona en la base de datos con múltiples embeddings
def recognize_person(face_img, database, model_name="Facenet", threshold=0.5):
    embedding_result = DeepFace.represent(img_path=face_img, model_name=model_name, enforce_detection=False)
    if not embedding_result:
        return "No se pudo generar el embedding."

    new_embedding = embedding_result[0]["embedding"]
    recognized_name = None
    min_distance = float("inf")

    # Comparar con cada persona en la base de datos
    for name, embeddings in database.items():
        for embedding in embeddings:
            distance = cosine(new_embedding, embedding)
            if distance < min_distance and distance < threshold:
                min_distance = distance
                recognized_name = name

    if recognized_name:
        return recognized_name, min_distance
    else:
        return "Desconocido", None

# Inicializar la captura de video desde la cámara del PC
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    # Capturar frame por frame desde la cámara del PC
    ret, frame = cap.read()
    if not ret:
        print("No se pudo recibir el frame. Finalizando transmisión...")
        break
    
    # Convertir a escala de grises para la detección de rostros
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Para cada rostro detectado, recortarlo y reconocerlo
    for (x, y, w, h) in faces:
        face_img = frame[y:y+h, x:x+w]
        
        # Guardar el recorte temporalmente para reconocimiento
        cv2.imwrite("temp_face.jpg", face_img)
        
        # Reconocimiento facial
        recognized_name, min_distance = recognize_person("temp_face.jpg", database)
        
        # Dibujar el rectángulo y poner el nombre en el frame de video
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        if recognized_name != "Desconocido":
            cv2.putText(frame, f"{recognized_name} ({min_distance:.2f})", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
            
            # Enviar a Magic Loops solo si no se ha enviado una notificación hoy
            if should_send_notification(recognized_name):
                send_to_magicloops(recognized_name, min_distance)
        else:
            cv2.putText(frame, "Desconocido", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # Mostrar el frame en la ventana
    cv2.imshow("Reconocimiento Facial en Tiempo Real", frame)
    
    # Para salir del bucle, presiona 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
