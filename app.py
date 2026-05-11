import os
import base64
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
# Permitir que tu frontend en React se comunique con este servidor
CORS(app, resources={r"/*": {"origins": "*"}})

# Configurar la IA de Google (La clave la pondremos en Railway)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # Usamos el modelo más rápido y avanzado para imágenes
    model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/analizar', methods=['POST'])
def analizar_imagen():
    if not GOOGLE_API_KEY:
        return jsonify({"error": "Falta la clave de la API de Google en el servidor"}), 500

    try:
        data = request.json
        base64_image = data.get('imagen')
        
        if not base64_image:
            return jsonify({"error": "No se envió ninguna imagen"}), 400

        # Limpiar el formato Base64 que envía React
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]

        # Convertir el texto Base64 a una Imagen real para la IA
        image_data = base64.b64decode(base64_image)
        image = Image.open(BytesIO(image_data))

        # 🧠 EL "PROMPT" (La instrucción para la IA)
        prompt = """
        Actúa como un despachador profesional de emergencias. 
        Analiza esta imagen y describe brevemente lo que ves en un máximo de 3 líneas. 
        Indica claramente qué tipo de emergencia es (accidente de tránsito, incendio, problema médico, robo, etc.) 
        y sugiere qué entidad debe responder (POLICIA, BOMBEROS o HOSPITAL). 
        Usa un tono urgente y formal.
        """

        # Enviar a la IA
        response = model.generate_content([prompt, image])

        # Devolver el análisis al Frontend
        return jsonify({"descripcion": response.text})

    except Exception as e:
        print("Error en IA:", e)
        return jsonify({"error": "Error interno del servidor IA"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)