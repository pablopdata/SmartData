from flask import Flask, render_template_string, redirect, url_for

from registro_diario import registro_bp

from solicitudes import solicitudes_bp

app = Flask(__name__)

# 🔹 Registro de Blueprints

app.register_blueprint(registro_bp, url_prefix="/registro")

app.register_blueprint(solicitudes_bp, url_prefix="/solicitudes")

# ==============================

# 🔹 PÁGINA PRINCIPAL

# ==============================

@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Panel Principal</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .dashboard-placeholder {
            height: 70vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #6c757d;
            font-size: 1.5rem;
            border: 2px dashed #ced4da;
            border-radius: 8px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <!-- Navbar superior -->
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <a class="navbar-brand" href="{{ url_for('index') }}">🧭 Panel Principal</a>
        <div class="ml-auto">
            <a href="{{ url_for('registro.ver_tabla') }}" class="btn btn-primary mr-2">📅 Registro Diario</a>
            <a href="{{ url_for('solicitudes.ver_solicitudes') }}" class="btn btn-success">📝 Solicitudes</a>
        </div>
    </nav>

    <!-- Contenedor principal -->
    <div class="container mt-4">
        <div class="dashboard-placeholder">
            Aquí irá el Dashboard de estadísticas 📊
        </div>
    </div>
</body>
</html>
    """)

# ==============================

# 🔹 REDIRECCIONES SIMPLES

# ==============================

@app.route("/inicio")

def inicio():

    return redirect(url_for("index"))

if __name__ == "__main__":

    app.run(debug=True)
 