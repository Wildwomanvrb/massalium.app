from flask import Flask, render_template, redirect, url_for, request, session
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import flash
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura_massalium'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Decorador para proteger rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Datos temporales (en memoria)
pacientes = []
citas = []
terapeutas = [
    {"nombre": "Klaudia", "especialidad": "Osteopatía"},
    {"nombre": "Alicia", "especialidad": "Masaje Deportivo"},
    {"nombre": "Pedro", "especialidad": "Quiromasaje"},
    {"nombre": "Diego", "especialidad": "Fisioterapia"}
]

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['username']
        clave = request.form['password']
        if usuario == 'massalium' and clave == 'admin123':
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

@app.route('/pacientes', methods=['GET', 'POST'])
@login_required
def pacientes_view():
    if request.method == 'POST':
        datos = request.form
        foto = request.files.get("foto")
        foto_filename = None

        if foto and foto.filename != '':
            filename = secure_filename(foto.filename)
            foto_filename = f"{datos['nombre']}_{datos['apellidos']}_{filename}"
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))

        paciente = {
            "nombre": datos.get("nombre"),
            "apellidos": datos.get("apellidos"),
            "sexo": datos.get("sexo"),
            "fecha_nacimiento": datos.get("fecha_nacimiento"),
            "terapeuta": datos.get("terapeuta"),
            "prefijo": datos.get("prefijo"),
            "telefono": datos.get("telefono"),
            "correo": datos.get("correo"),
            "motivo": datos.get("motivo"),
            "observaciones": datos.get("observaciones"),
            "importe": datos.get("importe"),
            "foto": foto_filename
        }
        pacientes.append(paciente)

        cita = {
            "paciente": f"{datos.get('nombre')} {datos.get('apellidos')}",
            "terapeuta": datos.get("terapeuta"),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "importe": datos.get("importe")
        }
        citas.append(cita)

        return redirect(url_for('pacientes_view'))

    return render_template('pacientes.html', pacientes=pacientes, terapeutas=[t['nombre'] for t in terapeutas], section='Pacientes')


@app.route('/guardar_paciente', methods=['POST'])
@login_required
def guardar_paciente():
    nombre = request.form['nombre']
    apellidos = request.form['apellidos']
    sexo = request.form['sexo']
    fecha_nacimiento = request.form['fecha_nacimiento']
    terapeuta = request.form['terapeuta']
    prefijo = request.form['prefijo']
    telefono = request.form['telefono']
    correo = request.form['correo']
    motivo = request.form['motivo']
    observaciones = request.form['observaciones']
    importe = request.form['importe']

    # Guardar la imagen
    foto = request.files['foto']
    nombre_archivo = ""
    if foto and foto.filename != '':
        nombre_archivo = secure_filename(foto.filename)
        ruta_guardado = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
        foto.save(ruta_guardado)

    nuevo_paciente = {
        'nombre': nombre,
        'apellidos': apellidos,
        'sexo': sexo,
        'fecha_nacimiento': fecha_nacimiento,
        'terapeuta': terapeuta,
        'telefono': f"{prefijo} {telefono}",
        'correo': correo,
        'motivo': motivo,
        'observaciones': observaciones,
        'importe': importe,
        'foto': nombre_archivo
    }

    pacientes.append(nuevo_paciente)

    # 🟡 Añadir al historial del terapeuta
    for t in terapeutas:
        if t['nombre'] == terapeuta:
            if 'historial' not in t:
                t['historial'] = []
            t['historial'].append({
                'nombre': nombre + ' ' + apellidos,
                'importe': importe,
                'fecha': datetime.today().strftime('%Y-%m-%d')
            })
    # Añadir la cita al historial general
    citas.append({
        'paciente': f"{nombre} {apellidos}",
        'terapeuta': terapeuta,
        'fecha': datetime.today().strftime('%Y-%m-%d'),
        'importe': importe
    })

    flash("Paciente guardado correctamente.")
    return redirect(url_for('pacientes_view'))


@app.route('/citas')
@login_required
def citas_view():
    return render_template('citas.html', section='Citas', citas=citas)

# --- Panel de historial de pacientes ---

@app.route('/historial', methods=['GET', 'POST'])
@login_required
def historial():
    filtro_fecha = request.args.get('fecha')
    filtro_importe = request.args.get('importe')

    historial_filtrado = citas.copy()
    if filtro_fecha:
        historial_filtrado = [c for c in historial_filtrado if filtro_fecha in c['fecha']]
    if filtro_importe:
        historial_filtrado = [c for c in historial_filtrado if float(c['importe']) >= float(filtro_importe)]

    return render_template('historial.html', citas=historial_filtrado, section='Historial')

@app.route('/historial/editar/<int:index>', methods=['GET', 'POST'])
@login_required
def editar_cita(index):
    if 0 <= index < len(citas):
        if request.method == 'POST':
            citas[index]['paciente'] = request.form['paciente']
            citas[index]['terapeuta'] = request.form['terapeuta']
            citas[index]['fecha'] = request.form['fecha']
            citas[index]['importe'] = request.form['importe']

            # Guardar imagen asociada a la cita
            imagen = request.files.get('imagen')
            if imagen and imagen.filename:
                nombre_imagen = secure_filename(imagen.filename)
                ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen)
                imagen.save(ruta_imagen)
                citas[index]['imagen'] = nombre_imagen

            return redirect(url_for('historial'))

        return render_template('editar_cita.html', cita=citas[index], index=index, section='Editar Cita')
    return redirect(url_for('historial'))

@app.route('/historial/eliminar/<int:index>')
@login_required
def eliminar_cita(index):
    if 0 <= index < len(citas):
        citas.pop(index)
    return redirect(url_for('historial'))

# --- Panel de gestión de terapeutas ---

@app.route('/terapeutas', methods=['GET', 'POST'])
@login_required
def terapeutas_view():
    if request.method == 'POST':
        nombre = request.form['nombre']
        especialidad = request.form['especialidad']
        foto = request.files.get('foto')
        nombre_foto = None

        if foto and foto.filename:
            nombre_foto = secure_filename(foto.filename)
            ruta_foto = os.path.join(app.config['UPLOAD_FOLDER'], nombre_foto)
            foto.save(ruta_foto)

        nuevo = {'nombre': nombre, 'especialidad': especialidad, 'foto': nombre_foto, 'historial': []}
        terapeutas.append(nuevo)
        return redirect(url_for('terapeutas_view'))

    return render_template('terapeutas.html', terapeutas=terapeutas, section='Terapeutas')

@app.route('/terapeutas/eliminar/<int:index>')
@login_required
def eliminar_terapeuta(index):
    if 0 <= index < len(terapeutas):
        terapeutas.pop(index)
    return redirect(url_for('terapeutas_view'))

@app.route('/terapeutas/editar/<int:index>', methods=['GET', 'POST'])
@login_required
def editar_terapeuta(index):
    if 0 <= index < len(terapeutas):
        if request.method == 'POST':
            terapeutas[index]['nombre'] = request.form['nombre']
            terapeutas[index]['especialidad'] = request.form['especialidad']
            foto = request.files.get('foto')
            if foto and foto.filename:
                nombre_foto = secure_filename(foto.filename)
                ruta_foto = os.path.join(app.config['UPLOAD_FOLDER'], nombre_foto)
                foto.save(ruta_foto)
                terapeutas[index]['foto'] = nombre_foto
            return redirect(url_for('terapeutas_view'))

        return render_template('editar_terapeuta.html', terapeuta=terapeutas[index], index=index, section='Editar Terapeuta')
    return redirect(url_for('terapeutas_view'))


@app.route('/membresias')
@login_required
def membresias():
    planes = [
        {"nombre": "GOLD", "descripcion": "1 sesión al mes", "precio": "49€/mes"},
        {"nombre": "PLATINUM", "descripcion": "2 sesiones al mes", "precio": "95€/mes"},
        {"nombre": "VIP", "descripcion": "3 sesiones al mes", "precio": "130€/mes"},
        {"nombre": "BLACK", "descripcion": "4 sesiones premium", "precio": "Precio exclusivo"}
    ]
    return render_template('membresias.html', section='Membresías', planes=planes)

@app.route('/estadisticas')
@login_required
def estadisticas():
    total_pacientes = len(pacientes)
    total_citas = len(citas)
    ingresos_totales = sum(float(c['importe']) for c in citas if c['importe'])

    return render_template(
        'estadisticas.html',
        section='Estadísticas',
        total_pacientes=total_pacientes,
        total_citas=total_citas,
        ingresos_totales=ingresos_totales
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)

