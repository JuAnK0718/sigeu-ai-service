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
        
        prompt = "Describe brevemente esta emergencia en máximo 3 líneas indicando si es necesaria POLICIA, BOMBEROS u HOSPITAL."
        
        # 🔥 LÓGICA BLINDADA: Lista de supervivencia
        # Dejamos el gemini-2.5-flash al puro final como último recurso.
        modelos_a_probar = [
            'gemini-2.0-flash',       # Nueva versión, muchísima cuota gratis
            'gemini-1.5-flash-8b',    # Versión súper ligera, casi imposible de agotar
            'gemini-1.5-pro',         # Versión inteligente antigua
            'gemini-2.5-flash'        # El que sabemos que te funciona pero solo da 20 intentos
        ]
        
        ultimo_error = ""
        
        for nombre_modelo in modelos_a_probar:
            try:
                print(f"Probando suerte con: {nombre_modelo}...")
                model = genai.GenerativeModel(nombre_modelo)
                response = model.generate_content([prompt, image])
                
                print(f"¡ÉXITO! Nos respondió el modelo: {nombre_modelo}")
                return jsonify({"descripcion": response.text})
                
            except Exception as e:
                # Si falla (por cuota o porque no existe), guardamos el error y el ciclo sigue
                ultimo_error = str(e)
                print(f"Falló {nombre_modelo} - Motivo: {ultimo_error[:60]}... ¡Pasando al siguiente!")
                continue 
                
        # Si el ciclo termina y TODOS los modelos de la lista fallaron
        print("Emergencia: Todos los modelos de Google rechazaron la foto.")
        return jsonify({"error": f"Límites de Google o modelos no encontrados. Último error: {ultimo_error}"}), 500

    except Exception as e:
        print(f"Error CRÍTICO de código: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)