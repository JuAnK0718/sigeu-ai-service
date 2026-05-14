import os
import base64
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
# Configuración CORS
CORS(app, resources={r"/*": {"origins": "*"}})

api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    genai.configure(api_key=api_key)

@app.route('/analizar', methods=['POST'])
def analizar_imagen():
    try:
        data = request.json
        base64_image = data.get('imagen')
        
        if not base64_image:
            return jsonify({"error": "No se envió ninguna imagen"}), 400

        # Limpiar la imagen
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]

        image_data = base64.b64decode(base64_image)
        image = Image.open(BytesIO(image_data))

        # 🚀 CÓDIGO CAZADOR DE MODELOS (Actualizado para evitar límites)
        print("--- Seleccionando modelo seguro de alta capacidad ---")
        
        # Obligamos a usar la versión 1.5 que tiene 1,500 peticiones diarias gratis
        modelo_elegido = 'gemini-1.5-flash' 
                    
        print(f"--- ¡Usando el modelo: {modelo_elegido}! ---")

        # Iniciar la IA con el modelo seguro
        model = genai.GenerativeModel(modelo_elegido)
        prompt = "Describe brevemente esta emergencia en máximo 3 líneas indicando si es necesaria POLICIA, BOMBEROS u HOSPITAL."
        
        response = model.generate_content([prompt, image])
        
        return jsonify({"descripcion": response.text})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)