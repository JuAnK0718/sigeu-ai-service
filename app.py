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

PROMPT_ANALISIS_EMERGENCIA = """
Analiza la imagen como apoyo operativo para SIGEU.
Responde en español claro, maximo 6 lineas, sin Markdown, sin asteriscos y sin adornos.
Incluye estos puntos cuando se puedan inferir visualmente:
Escena: describe que ocurre.
Riesgos: menciona posibles heridos, personas atrapadas, fuego, humo, via bloqueada, daño estructural o riesgo para peatones/vehiculos.
Gravedad: Baja, Media, Alta o Critica, con una razon breve.
Entidades: escribe exactamente POLICIA, BOMBEROS, HOSPITAL o NINGUNA EMERGENCIA segun corresponda.
Recursos sugeridos: indica cantidades aproximadas solo si hay señales claras; si no es claro, usa "posibles" o "por confirmar".
No inventes datos invisibles: si algo no se ve con certeza, dilo como posible.
"""

def limpiar_descripcion_ia(texto):
    texto = (texto or '').strip()
    if not texto:
        return "Escena: La imagen no permite identificar con claridad la emergencia.\nRiesgos: Por confirmar.\nGravedad: Media.\nEntidades: POLICIA."

    lineas = []
    for linea in texto.splitlines():
        limpia = linea.strip().lstrip('-•* ').strip()
        if limpia:
            lineas.append(limpia)

    descripcion = '\n'.join(lineas[:8]).strip()
    return descripcion[:1200]

@app.route('/analizar', methods=['POST'])
def analizar_imagen():
    try:
        data = request.get_json(silent=True) or {}
        base64_image = data.get('imagen')
        
        if not base64_image:
            return jsonify({"error": "No se envió ninguna imagen"}), 400

        # Limpiar la imagen
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]

        image_data = base64.b64decode(base64_image)
        image = Image.open(BytesIO(image_data))

        
        print("--- Buscando modelos disponibles en tu API Key ---")
        modelo_elegido = 'gemini-1.5-flash' # Modelo por defecto
        
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Modelo detectado: {m.name}")
                # Buscamos dinámicamente uno que sirva para imágenes
                if 'flash' in m.name:
                    modelo_elegido = m.name
                    break
                    
        print(f"--- ¡Usando el modelo: {modelo_elegido}! ---")

        # Iniciar la IA con el modelo seguro
        model = genai.GenerativeModel(modelo_elegido)
        
        response = model.generate_content([PROMPT_ANALISIS_EMERGENCIA, image])
        descripcion = limpiar_descripcion_ia(response.text)
        
        return jsonify({"descripcion": descripcion})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
