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
<html>
<head>
<title>Panel Principal</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container text-center mt-5">
<h1 class="mb-4">🧭 Panel Principal</h1>
<div class="list-group">
<a href="{{ url_for('registro.ver_registro') }}" class="list-group-item list-group-item-action list-group-item-primary">📅 Registro Diario</a>
<a href="{{ url_for('solicitudes.ver_solicitudes') }}" class="list-group-item list-group-item-action list-group-item-success">📝 Solicitudes</a>
</div>
<br>
<footer class="text-muted mt-5">Desarrollado por José Enrique Gallego</footer>
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
 