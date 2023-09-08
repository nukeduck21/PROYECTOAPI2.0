from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar Firebase Admin SDK (reemplaza 'ruta/a/tu/archivo-de-configuracion.json' con la ruta correcta)
cred = credentials.Certificate("imc-api-2-firebase-adminsdk-rljxf-df411d520c.json")
firebase_admin.initialize_app(cred)

# Conectar con Firestore
db = firestore.client()

app = Flask(__name__, template_folder='templates')  # Aquí configuramos la carpeta de plantillas

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular-imc', methods=['POST'])
def calcular_imc():
    try:
        data = request.get_json()
        correo = data['correo']
        peso = data['peso']
        altura = data['altura']

        # Calcular el IMC
        imc = peso / (altura ** 2)

        # Determinar la categoría del IMC
        if imc < 18.5:
            categoria = "Flaco"
        elif imc >= 18.5 and imc < 24.9:
            categoria = "En forma"
        else:
            categoria = "Gordo"

        # Guardar los datos en Firestore
        usuario_ref = db.collection('usuarios').document(correo)
        usuario_ref.set({
            'peso': peso,
            'altura': altura,
            'imc': imc,
            'categoria': categoria
        })

        # Enviar una respuesta JSON
        respuesta = {
            'mensaje': 'Tu IMC ha sido calculado y registrado con éxito.',
            'imc': imc,
            'categoria': categoria
        }

        return jsonify(respuesta), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

