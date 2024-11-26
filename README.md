# Reconocimiento Facial en Tiempo Real con Notificación a Magic Loops
Este proyecto realiza el reconocimiento facial en tiempo real utilizando la biblioteca OpenCV para detectar rostros y la librería deepface para el reconocimiento. Además, al identificar a una persona previamente registrada, se envía una notificación a través de un webhook a Magic Loops. Las notificaciones se envían solo una vez por día para cada persona.
## Requisitos
- **Python 3.x**
- **OpenCV (cv2)**
- **DeepFace**
- **Requests**
- **Numpy**
- **SciPy**

## Resumen discripcion de codigo
### Principales Funciones
- **Reconocimiento Facial**: El código captura imágenes de la cámara web en tiempo real y utiliza el modelo Facenet de DeepFace para generar un "embedding" (vector de características) de cada rostro detectado.

- **Base de Datos de Rostros**: Se utiliza un diccionario llamado database que contiene nombres y las rutas a las imágenes de referencia para cada persona. Los embeddings de estas imágenes se generan y se almacenan para su posterior comparación con los rostros detectados en tiempo real.

- **Comparación de Rostros**: Al detectar un rostro, el código genera un embedding y lo compara con los embeddings en la base de datos usando la distancia de Coseno. Si la distancia es inferior al umbral (por defecto 0.5), se reconoce a la persona.

- **Envío de Notificación a Magic Loops**: Si se detecta a una persona y no se ha enviado una notificación hoy, el código realiza una solicitud HTTP GET al webhook de Magic Loops con un mensaje personalizado que incluye el nombre de la persona y la distancia de similitud entre los embeddings.

- **Lógica de Envío Condicional**: El código mantiene un registro de las personas que ya han recibido una notificación el mismo día para evitar enviar múltiples alertas

### Instrucciones de uso
- Asegúrate de tener las imágenes de referencia de las personas que deseas reconocer en una carpeta local.

- Actualiza la variable reference_images en el código para incluir las rutas de tus imágenes de referencia, y asigna un nombre a cada persona:
  ```Python
  reference_images = {
    "persona1": ["ruta_imagen1.jpg", "ruta_imagen2.jpg"],
    "persona2": ["ruta_imagen3.jpg", "ruta_imagen4.jpg"]
  }
  ```
- Cambia la URL del webhook de Magic Loops, en la variable magicloops_url.
  ```Python
  # Configuración de la URL de Magic Loops
  magicloops_url = "https://magicloops.dev/api/loop/run/4104dda6-72f6-452c-a4af-f5b32d8cd0e6"
  ```
### Archivos del Proyecto
- reconocimiento_facial.py: Script principal que realiza la captura de video, reconocimiento facial y envío de notificaciones.
- haarcascade_frontalface_default.xml: Archivo de clasificación en cascada de OpenCV para la detección de rostros.

### Notas

- El modelo de DeepFace Facenet se utiliza para el reconocimiento facial. Puedes cambiar el modelo si lo prefieres (por ejemplo, VGG-Face, OpenFace, etc.).
- El umbral de similitud de rostros está configurado en 0.5, pero puedes ajustarlo para hacer el reconocimiento más o menos estricto.
- El sistema solo enviará una notificación al día por persona.
  
