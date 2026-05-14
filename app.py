import os
import base64
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
# Configuración CORS ultra permisiva
CORS(app, resources={r"/*": {"origins": "*"}})

# Cargar API Key de forma segura
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

        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]

        image_data = base64.b64decode(base64_image)
        image = Image.open(BytesIO(image_data))

        # 🚀 LÓGICA ROBUSTA CON PLAN B
        prompt = "Describe brevemente esta emergencia en máximo 3 líneas indicando si es necesaria POLICIA, BOMBEROS u HOSPITAL."
        
        try:
            # INTENTO 1: Usamos la versión estable y de alta cuota (gemini-1.5-flash-latest)
            modelo_primario = 'gemini-1.5-flash-latest'
            print(f"--- Intentando con modelo primario: {modelo_primario} ---")
            model = genai.GenerativeModel(modelo_primario)
            response = model.generate_content([prompt, image])
            
            return jsonify({"descripcion": response.text})
            
        except Exception as e_primario:
            # Si el primario falla (404, 429, etc.), usamos el PLAN B automáticamente
            error_string = str(e_primario)
            print(f"--- Falla en primario: {error_string}. Activando PLAN B ---")
            
            # PLAN B: Usamos gemini-pro que es multimodal y muy compatible
            # (Aunque tiene cuota menor, es mejor que un error 404)
            modelo_backup = 'gemini-pro' 
            model = genai.GenerativeModel(modelo_backup)
            
            # Nota: gemini-pro a veces requiere una estructura distinta para imágenes
            # dependiendo de la versión del SDK, pero generate_content suele ser compatible.
            response = model.generate_content([prompt, image])
            
            return jsonify({
                "descripcion": response.text,
                "nota": "Se usó modelo de respaldo por inestabilidad de Google API."
            })

    except Exception as e:
        print(f"Error CRÍTICO Final: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)