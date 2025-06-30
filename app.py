from flask import Flask, render_template, redirect, url_for, request, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura_massalium'

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    return redirect(url_for('login'))

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
