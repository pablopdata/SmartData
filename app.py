from flask import Flask, render_template_string, Response, request, redirect, url_for

import matplotlib.pyplot as plt

import io

import os

from supabase import create_client, Client

app = Flask(__name__)

# 🔗 Configuración desde variables de entorno

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializa el cliente de Supabase

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# 🔹 Función general para obtener datos desde Supabase

def get_data(tabla):

    """Obtiene los datos desde una tabla de Supabase"""

    try:

        response = supabase.table(tabla).select("*").execute()

        print(f"📊 Datos obtenidos de {tabla}: {response.data}")

        return response.data

    except Exception as e:

        print(f"❌ Error obteniendo datos de {tabla}: {e}")

        return []


# 🔹 Página principal: Imputaciones

@app.route("/", methods=["GET", "POST"])

def index():

    if request.method == "POST":

        codigo = request.form.get("codigo")

        horas_totales = request.form.get("horas_totales")

        if codigo and horas_totales:

            try:

                supabase.table("imputaciones").insert({

                    "codigo": codigo,

                    "horas_totales": int(horas_totales)

                }).execute()

                print(f"✅ Insertado: {codigo}, {horas_totales}")

            except Exception as e:

                print("❌ Error insertando registro:", e)

        return redirect(url_for("index"))

    data = get_data("imputaciones")

    if not data:

        table_rows = "<tr><td colspan='3'>No hay datos disponibles o error de conexión</td></tr>"

    else:

        table_rows = "".join(

            f"<tr><td>{row.get('id', '')}</td><td>{row.get('codigo', '')}</td><td>{row.get('horas_totales', '')}</td></tr>"

            for row in data

        )

    return render_template_string("""
<html>
<head>
<title>Imputaciones Smart Data</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
<style>

body { font-family: 'Arial', sans-serif; background-color: #f4f4f9; }

.container { margin-top: 50px; }

h1 { color: #333; text-align: center; margin-bottom: 40px; }

.table-container { max-height: 400px; overflow-y: auto; }

.img-fluid { max-height: 400px; }

.refresh-btn, .add-btn {

    display: block;

    margin: 10px auto;

    background-color: #007bff;

    border: none;

    color: white;

    padding: 10px 25px;

    border-radius: 5px;

    font-size: 16px;

    cursor: pointer;

}

.refresh-btn:hover, .add-btn:hover { background-color: #0056b3; }
</style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
<a class="navbar-brand" href="#">IMPUTACIONES SMART DATA</a>
<div class="ml-auto">
<a href="{{ url_for('ver_tabla') }}" class="btn btn-outline-light">📋 Ver Registro Diario</a>
</div>
</nav>
<div class="container">
<h1>Resumen de Imputaciones</h1>
<button class="refresh-btn" onclick="refreshData()">🔄 Refrescar Datos</button>
<form method="POST" class="text-center mb-3">
<input type="text" name="codigo" placeholder="Código" required style="margin-right:10px;padding:5px;">
<input type="number" name="horas_totales" placeholder="Horas Totales" required style="margin-right:10px;padding:5px;">
<button type="submit" class="add-btn">➕ Añadir Registro</button>
</form>
<div class="row">
<div class="col-md-6">
<div class="table-container">
<table class="table table-striped table-bordered">
<thead class="thead-dark">
<tr><th>ID</th><th>Código</th><th>Horas Totales</th></tr>
</thead>
<tbody id="data-table">

    {{ table_rows|safe }}
</tbody>
</table>
</div>
</div>
<div class="col-md-6 text-center">
<img id="chart" src="{{ url_for('plot_png') }}" alt="Gráfico de Tarta" class="img-fluid">
<p class="mt-3">Horas Imputadas vs Horas Totales</p>
</div>
</div>
</div>
<script>

function refreshData() {

    fetch(window.location.href)

      .then(response => response.text())

      .then(html => {

          const parser = new DOMParser();

          const doc = parser.parseFromString(html, "text/html");

          document.getElementById("data-table").innerHTML =

              doc.getElementById("data-table").innerHTML;

      });

    const chart = document.getElementById("chart");

    chart.src = "/plot.png?" + new Date().getTime();

}
</script>
</body>
</html>

""", table_rows=table_rows)


# 🔹 CRUD: Registro Diario

@app.route("/ver_tabla")

def ver_tabla():

    try:

        response = supabase.table("registro_diario").select("*").order("fecha", desc=True).execute()

        data = response.data

        print("DEBUG registro_diario:", data)

    except Exception as e:

        print(f"❌ Error obteniendo datos de registro_diario: {e}")

        data = []

    if not data:

        table_rows = "<tr><td colspan='8'>No hay datos disponibles o error de conexión</td></tr>"

    else:

        table_rows = "".join(

            f"<tr>"

            f"<td>{row.get('fecha', '')}</td>"

            f"<td>{row.get('tarea', '')}</td>"

            f"<td>{row.get('persona', '')}</td>"

            f"<td>{row.get('horas', '')}</td>"

            f"<td>{row.get('peticion', '')}</td>"

            f"<td>{row.get('porcentaje_real', '')}</td>"

            f"<td>{row.get('porcentaje_nvs', '')}</td>"

            f"<td>"

            f"<a href='/editar_registro/{row.get('id')}' class='btn btn-warning btn-sm'>✏️ Editar</a> "

            f"<a href='/eliminar_registro/{row.get('id')}' class='btn btn-danger btn-sm' "

            f"onclick='return confirm(\"¿Seguro que quieres eliminar este registro?\")'>🗑️ Eliminar</a>"

            f"</td>"

            f"</tr>"

            for row in data

        )

    return render_template_string("""
<html>
<head>
<title>Registro Diario</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
<a class="navbar-brand" href="{{ url_for('index') }}">← Volver</a>
<span class="navbar-text ml-3 text-white">Vista del Registro Diario</span>
</nav>
<div class="container mt-5">
<h2 class="mb-4">Tabla registro_diario</h2>
<form method="POST" action="/crear_registro" class="mb-4">
<div class="form-row">
<div class="col"><input type="date" name="fecha" class="form-control" required></div>
<div class="col"><input type="text" name="tarea" class="form-control" placeholder="Tarea" required></div>
<div class="col"><input type="text" name="persona" class="form-control" placeholder="Persona" required></div>
<div class="col"><input type="number" step="0.1" name="horas" class="form-control" placeholder="Horas" required></div>
<div class="col"><input type="text" name="peticion" class="form-control" placeholder="Petición"></div>
<div class="col"><input type="number" name="porcentaje_real" class="form-control" placeholder="% Real"></div>
<div class="col"><input type="number" name="porcentaje_nvs" class="form-control" placeholder="% NVS"></div>
<div class="col"><button type="submit" class="btn btn-success">➕ Añadir</button></div>
</div>
</form>
<div class="table-responsive">
<table class="table table-striped table-bordered">
<thead class="thead-dark">
<tr>
<th>fecha</th>
<th>tarea</th>
<th>persona</th>
<th>horas</th>
<th>peticion</th>
<th>porcentaje_real</th>
<th>porcentaje_nvs</th>
<th>Acciones</th>
</tr>
</thead>
<tbody>

    {{ table_rows|safe }}
</tbody>
</table>
</div>
</div>
</body>
</html>

""", table_rows=table_rows)


# 🔹 Crear registro

@app.route("/crear_registro", methods=["POST"])

def crear_registro():

    data = {

        "fecha": request.form.get("fecha"),

        "tarea": request.form.get("tarea"),

        "persona": request.form.get("persona"),

        "horas": float(request.form.get("horas")),

        "peticion": request.form.get("peticion"),

        "porcentaje_real": request.form.get("porcentaje_real"),

        "porcentaje_nvs": request.form.get("porcentaje_nvs")

    }

    try:

        supabase.table("registro_diario").insert(data).execute()

        print("✅ Registro creado correctamente:", data)

    except Exception as e:

        print("❌ Error al crear registro:", e)

    return redirect(url_for("ver_tabla"))


# 🔹 Editar registro

@app.route("/editar_registro/<int:registro_id>", methods=["GET", "POST"])

def editar_registro(registro_id):

    if request.method == "POST":

        data = {

            "fecha": request.form.get("fecha"),

            "tarea": request.form.get("tarea"),

            "persona": request.form.get("persona"),

            "horas": float(request.form.get("horas")),

            "peticion": request.form.get("peticion"),

            "porcentaje_real": request.form.get("porcentaje_real"),

            "porcentaje_nvs": request.form.get("porcentaje_nvs")

        }

        try:

            supabase.table("registro_diario").update(data).eq("id", registro_id).execute()

            print(f"✏️ Registro {registro_id} actualizado correctamente")

        except Exception as e:

            print("❌ Error al actualizar registro:", e)

        return redirect(url_for("ver_tabla"))

    response = supabase.table("registro_diario").select("*").eq("id", registro_id).single().execute()

    registro = response.data

    if not registro:

        return f"<h3>No se encontró el registro con ID {registro_id}</h3>"

    return render_template_string("""
<html>
<head>
<title>Editar Registro</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-5">
<h2>Editar Registro Diario</h2>
<form method="POST">
<input type="date" name="fecha" value="{{ registro['fecha'] }}" class="form-control mb-2" required>
<input type="text" name="tarea" value="{{ registro['tarea'] }}" class="form-control mb-2" required>
<input type="text" name="persona" value="{{ registro['persona'] }}" class="form-control mb-2" required>
<input type="number" step="0.1" name="horas" value="{{ registro['horas'] }}" class="form-control mb-2" required>
<input type="text" name="peticion" value="{{ registro['peticion'] }}" class="form-control mb-2">
<input type="number" name="porcentaje_real" value="{{ registro['porcentaje_real'] }}" class="form-control mb-2">
<input type="number" name="porcentaje_nvs" value="{{ registro['porcentaje_nvs'] }}" class="form-control mb-2">
<button type="submit" class="btn btn-primary">💾 Guardar Cambios</button>
<a href="{{ url_for('ver_tabla') }}" class="btn btn-secondary">Cancelar</a>
</form>
</body>
</html>

    """, registro=registro)


# 🔹 Eliminar registro

@app.route("/eliminar_registro/<int:registro_id>")

def eliminar_registro(registro_id):

    try:

        supabase.table("registro_diario").delete().eq("id", registro_id).execute()

        print(f"🗑️ Registro {registro_id} eliminado correctamente")

    except Exception as e:

        print("❌ Error al eliminar registro:", e)

    return redirect(url_for("ver_tabla"))


# 🔹 Gráfico circular

@app.route("/plot.png")

def plot_png():

    data = get_data("imputaciones")

    horas_imputadas = sum(d.get('horas_totales', 0) for d in data) if data else 0

    horas_totales = 16

    restantes = max(horas_totales - horas_imputadas, 0)

    labels = ['Horas Imputadas', 'Horas Restantes']

    sizes = [horas_imputadas, restantes]

    colors = ['#007bff', '#cccccc']

    fig, ax = plt.subplots()

    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)

    ax.axis('equal')

    plt.title("Distribución de Horas")

    output = io.BytesIO()

    fig.savefig(output, format="png", bbox_inches='tight')

    plt.close(fig)

    output.seek(0)

    return Response(output.getvalue(), mimetype="image/png")


# 🔹 Ejecución

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
 

