from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Inicializar Firebase Admin SDK (reemplaza 'ruta/a/tu/archivo-de-configuracion.json' con la ruta correcta)
cred = credentials.Certificate("api-correo-aaeb7-firebase-adminsdk-c0ea6ba41c.json")
firebase_admin.initialize_app(cred)

# Conectar con Firestore
db = firestore.client()

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configura la información de tu servidor SMTP para enviar correos
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "lucio3143187070@gmail.com"
smtp_password = "bzugjpwmylttkqev"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular-imc', methods=['POST'])
def calcular_imc():
    try:
        data = request.form
        correo = data['correo']
        peso = float(data['peso'])
        altura = float(data['altura'])

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

        # Enviar correo electrónico con la categoría del IMC
        enviar_correo(correo, imc, categoria)

        return render_template('resultado.html', imc=imc, categoria=categoria)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def enviar_correo(destinatario, imc, categoria):
    try:
        # Configurar el correo
        mensaje = MIMEMultipart()
        mensaje['From'] = smtp_username
        mensaje['To'] = destinatario
        mensaje['Subject'] = "Resultado del IMC"

        # Cuerpo del correo
        cuerpo = f"Tu IMC es {imc:.2f}, lo que te clasifica como {categoria}."
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        # Conectar al servidor SMTP y enviar el correo
        servidor_smtp = smtplib.SMTP(smtp_server, smtp_port)
        servidor_smtp.starttls()
        servidor_smtp.login(smtp_username, smtp_password)
        servidor_smtp.sendmail(smtp_username, destinatario, mensaje.as_string())
        servidor_smtp.quit()

    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
