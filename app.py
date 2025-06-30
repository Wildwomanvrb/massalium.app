from flask import Flask, render_template, redirect, url_for, request, session
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura_massalium'

app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Crear carpeta para subir imágenes si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Datos temporales
pacientes = []
citas = []
terapeutas = ["Klaudia", "Alicia", "Pedro", "Diego"]

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route("/pacientes", methods=["GET", "POST"])
def pacientes_view():
    if request.method == "POST":
        datos = request.form
        foto = request.files.get("foto")
        foto_filename = None

        if foto:
            foto_filename = secure_filename(f"{datos['nombre']}_{datos['apellidos']}_{foto.filename}")
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))

        paciente = {
            "nombre": datos["nombre"],
            "apellidos": datos["apellidos"],
            "sexo": datos["sexo"],
            "fecha_nacimiento": datos["fecha_nacimiento"],
            "terapeuta": datos["terapeuta"],
            "prefijo": datos["prefijo"],
            "telefono": datos["telefono"],
            "correo": datos["correo"],
            "motivo": datos["motivo"],
            "observaciones": datos["observaciones"],
            "importe": datos["importe"],
            "foto": foto_filename
        }
        pacientes.append(paciente)

        cita = {
            "paciente": f"{datos['nombre']} {datos['apellidos']}",
            "terapeuta": datos["terapeuta"],
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "hora": datetime.now().strftime("%H:%M"),
            "importe": datos["importe"]
        }
        citas.append(cita)

        return redirect(url_for("pacientes_view"))

    return render_template("pacientes.html", terapeutas=terapeutas, pacientes=pacientes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'massalium' and request.form['password'] == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Credenciales incorrectas')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', section='Inicio')

@app.route('/pacientes')
@login_required
def pacientes():
    return render_template('pacientes.html', section='Pacientes')

@app.route('/citas')
@login_required
def citas():
    return render_template('citas.html', section='Citas')

@app.route('/historial')
@login_required
def historial():
    return render_template('historial.html', section='Historial')

@app.route('/terapeutas')
@login_required
def terapeutas():
    return render_template('terapeutas.html', section='Terapeutas')

@app.route('/membresias')
@login_required
def membresias():
    return render_template('membresias.html', section='Membresías')

@app.route('/estadisticas')
@login_required
def estadisticas():
    return render_template('estadisticas.html', section='Estadísticas')

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

