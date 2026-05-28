# SIGEU AI Service

SIGEU AI Service es el servicio independiente de inteligencia artificial del Sistema Inteligente de Gestion de Emergencias Urbanas. Su funcion principal es analizar imagenes enviadas desde el frontend y generar una descripcion operativa del incidente para apoyar la clasificacion y priorizacion de emergencias.

El servicio se comunica con el frontend mediante una API HTTP y utiliza Gemini como modelo de analisis visual.

## Objetivo

El objetivo del servicio es complementar el reporte ciudadano con una interpretacion automatica de la evidencia visual. El analisis generado ayuda a identificar la escena, posibles riesgos, gravedad aproximada, entidades recomendadas y recursos sugeridos cuando la imagen lo permite.

## Arquitectura

El servicio esta separado del backend principal de SIGEU. Esta separacion permite que el analisis de imagenes funcione como un modulo independiente, manteniendo desacopladas la inteligencia artificial, la gestion de datos y la interfaz de usuario.

Flujo general:

1. El ciudadano adjunta una imagen desde el frontend.
2. El frontend convierte la imagen a base64.
3. La imagen se envia al endpoint `/analizar`.
4. El servicio procesa la imagen con Gemini.
5. La API devuelve una descripcion estructurada al frontend.
6. El reporte final se envia al backend de SIGEU.

## Tecnologias

- Python 3.11.9
- Flask
- Flask-CORS
- Google Generative AI SDK
- Gemini
- Pillow
- Gunicorn
- Railway para despliegue

# SIGEU AI Service

Microservicio de inteligencia artificial para clasificación de emergencias urbanas.

## Tecnologías
- Python
- FastAPI

## Instalación

pip install -r requirements.txt

## Ejecutar

uvicorn main:app --reload

## Endpoints
- POST /classify - Clasifica el tipo de emergencia (policía, ambulancia, bomberos)
- GET /health - Estado del servicio
## Endpoint principal

### Analizar imagen

`POST /analizar`

Solicitud:

```json
{
  "imagen": "data:image/jpeg;base64,..."
}
```

La imagen tambien puede enviarse como cadena base64 sin encabezado `data:image`.

Respuesta exitosa:

```json
{
  "descripcion": "Escena: ...\nRiesgos: ...\nGravedad: ...\nEntidades: ..."
}
```

Respuesta de error:

```json
{
  "error": "No se envio ninguna imagen"
}
```

## Analisis generado

El prompt del servicio solicita una respuesta breve en espanol con informacion operativa:

- Escena observada.
- Posibles riesgos visibles.
- Gravedad aproximada: Baja, Media, Alta o Critica.
- Entidades recomendadas: POLICIA, BOMBEROS, HOSPITAL o NINGUNA EMERGENCIA.
- Recursos sugeridos cuando existan senales claras en la imagen.

El servicio evita inventar informacion no visible y expresa como posible aquello que no pueda confirmarse por la imagen.

## Variables de entorno

Configuracion principal:

```env
GOOGLE_API_KEY=your-google-api-key
PORT=8080
```

`GOOGLE_API_KEY` permite conectar el servicio con Gemini. La clave se configura como variable de entorno y no debe almacenarse en el codigo fuente.

## Despliegue

El servicio esta preparado para ejecutarse con Gunicorn:

```text
web: gunicorn --bind 0.0.0.0:$PORT --timeout 120 app:app
```

Railway proporciona la variable `PORT` durante el despliegue. El frontend consume el servicio mediante la variable `VITE_AI_SERVICE_URL`.

## Integracion con SIGEU

Este servicio no registra reportes ni accede directamente a la base de datos. Su responsabilidad se limita al analisis de imagenes. La persistencia de reportes, usuarios, estados y recursos se mantiene en el backend principal de SIGEU.

## Consideraciones tecnicas

- El analisis de IA se utiliza como apoyo operativo, no como decision definitiva.
- La descripcion generada se limita en longitud antes de enviarse al frontend.
- El servicio limpia caracteres de formato innecesarios para devolver una respuesta clara.
- Si la imagen no permite identificar una emergencia con claridad, se devuelve una respuesta de respaldo.
