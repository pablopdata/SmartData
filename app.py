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

# 🔹 Página principal

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
<a href="{{ url_for('ver_solicitudes') }}" class="btn btn-outline-warning ml-2">📄 Ver Solicitudes</a>
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

# 🔹 CRUD: REGISTRO_DIARIO

@app.route("/ver_tabla")

def ver_tabla():

    try:

        response = supabase.table("registro_diario").select("*").order("fecha", desc=True).execute()

        data = response.data

    except Exception as e:

        print(f"❌ Error obteniendo datos: {e}")

        data = []

    if not data:

        table_rows = "<tr><td colspan='8'>No hay datos disponibles</td></tr>"

    else:

        table_rows = "".join(

            f"<tr>"

            f"<td>{row.get('fecha','')}</td><td>{row.get('tarea','')}</td><td>{row.get('persona','')}</td>"

            f"<td>{row.get('horas','')}</td><td>{row.get('peticion','')}</td>"

            f"<td>{row.get('porcentaje_real','')}</td><td>{row.get('porcentaje_nvs','')}</td>"

            f"<td><a href='/editar_registro/{row.get('id')}' class='btn btn-warning btn-sm'>✏️</a> "

            f"<a href='/eliminar_registro/{row.get('id')}' class='btn btn-danger btn-sm'>🗑️</a></td></tr>"

            for row in data

        )

    return render_template_string("""
<html><head><title>Registro Diario</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet"></head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
<a class="navbar-brand" href="{{ url_for('index') }}">← Volver</a>
</nav>
<div class="container mt-5">
<h2>Tabla registro_diario</h2>
<form method="POST" action="/crear_registro" class="mb-4">
<div class="form-row">
<div class="col"><input type="date" name="fecha" class="form-control" required></div>
<div class="col"><input type="text" name="tarea" placeholder="Tarea" class="form-control" required></div>
<div class="col"><input type="text" name="persona" placeholder="Persona" class="form-control" required></div>
<div class="col"><input type="number" step="0.1" name="horas" placeholder="Horas" class="form-control" required></div>
<div class="col"><input type="text" name="peticion" placeholder="Petición" class="form-control"></div>
<div class="col"><input type="number" name="porcentaje_real" placeholder="% Real" class="form-control"></div>
<div class="col"><input type="number" name="porcentaje_nvs" placeholder="% NVS" class="form-control"></div>
<div class="col"><button type="submit" class="btn btn-success">➕ Añadir</button></div>
</div></form>
<table class="table table-striped table-bordered"><thead class="thead-dark">
<tr><th>Fecha</th><th>Tarea</th><th>Persona</th><th>Horas</th><th>Petición</th><th>% Real</th><th>% NVS</th><th>Acciones</th></tr>
</thead><tbody>{{ table_rows|safe }}</tbody></table></div></body></html>

""", table_rows=table_rows)

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

    supabase.table("registro_diario").insert(data).execute()

    return redirect(url_for("ver_tabla"))

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

        supabase.table("registro_diario").update(data).eq("id", registro_id).execute()

        return redirect(url_for("ver_tabla"))

    registro = supabase.table("registro_diario").select("*").eq("id", registro_id).single().execute().data

    return render_template_string("""
<html><head><title>Editar Registro</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="p-5"><h2>Editar Registro Diario</h2>
<form method="POST">
<input type="date" name="fecha" value="{{ registro['fecha'] }}" class="form-control mb-2" required>
<input type="text" name="tarea" value="{{ registro['tarea'] }}" class="form-control mb-2" required>
<input type="text" name="persona" value="{{ registro['persona'] }}" class="form-control mb-2" required>
<input type="number" step="0.1" name="horas" value="{{ registro['horas'] }}" class="form-control mb-2" required>
<input type="text" name="peticion" value="{{ registro['peticion'] }}" class="form-control mb-2">
<input type="number" name="porcentaje_real" value="{{ registro['porcentaje_real'] }}" class="form-control mb-2">
<input type="number" name="porcentaje_nvs" value="{{ registro['porcentaje_nvs'] }}" class="form-control mb-2">
<button type="submit" class="btn btn-primary">💾 Guardar</button>
<a href="{{ url_for('ver_tabla') }}" class="btn btn-secondary">Cancelar</a></form></body></html>

""", registro=registro)

@app.route("/eliminar_registro/<int:registro_id>")

def eliminar_registro(registro_id):

    supabase.table("registro_diario").delete().eq("id", registro_id).execute()

    return redirect(url_for("ver_tabla"))

# 🔹 CRUD: SOLICITUDES

@app.route("/ver_solicitudes")
def ver_solicitudes():
   try:
       response = supabase.table("solicitudes").select("*").order("id_solicitud", desc=True).execute()
       data = response.data
       print("DEBUG solicitudes:", data)
   except Exception as e:
       print(f"❌ Error obteniendo datos de solicitudes: {e}")
       data = []
   if not data:
       table_rows = "<tr><td colspan='10'>No hay datos disponibles o error de conexión</td></tr>"
   else:
       table_rows = "".join(
           f"<tr>"
           f"<td>{row.get('id_solicitud', '')}</td>"
           f"<td>{row.get('solicitud', '')}</td>"
           f"<td>{row.get('url_nvs', '')}</td>"
           f"<td>{row.get('peticion', '')}</td>"
           f"<td>{row.get('id_moda', '')}</td>"
           f"<td>{row.get('url_moda', '')}</td>"
           f"<td>{row.get('horas_totales', '')}</td>"
           f"<td>{row.get('fecha_inicio', '')}</td>"
           f"<td>{row.get('fecha_fin', '')}</td>"
           f"<td>{'✅' if row.get('completada') else '❌'}</td>"
           f"<td>"
           f"<a href='/editar_solicitud/{row.get('id_solicitud')}' class='btn btn-warning btn-sm'>✏️ Editar</a> "
           f"<a href='/eliminar_solicitud/{row.get('id_solicitud')}' class='btn btn-danger btn-sm' "
           f"onclick='return confirm(\"¿Seguro que quieres eliminar esta solicitud?\")'>🗑️ Eliminar</a>"
           f"</td></tr>"
           for row in data
       )
   return render_template_string("""
<html>
<head>
<title>Solicitudes</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
<a class="navbar-brand" href="{{ url_for('index') }}">← Volver</a>
<span class="navbar-text ml-3 text-white">Gestión de Solicitudes</span>
</nav>
<div class="container mt-5">
<h2 class="mb-4">Tabla de Solicitudes</h2>
<form method="POST" action="/crear_solicitud" class="mb-4">
<div class="form-row">
<div class="col"><input type="text" name="solicitud" class="form-control" placeholder="Solicitud" required></div>
<div class="col"><input type="text" name="url_nvs" class="form-control" placeholder="URL NVS"></div>
<div class="col"><input type="text" name="peticion" class="form-control" placeholder="Petición"></div>
<div class="col"><input type="text" name="id_moda" class="form-control" placeholder="ID Moda"></div>
<div class="col"><input type="text" name="url_moda" class="form-control" placeholder="URL Moda"></div>
</div>
<div class="form-row mt-2">
<div class="col"><input type="number" step="0.1" name="horas_totales" class="form-control" placeholder="Horas Totales"></div>
<div class="col"><input type="date" name="fecha_inicio" class="form-control"></div>
<div class="col"><input type="date" name="fecha_fin" class="form-control"></div>
<div class="col">
<select name="completada" class="form-control">
<option value="false">❌ No Completada</option>
<option value="true">✅ Completada</option>
</select>
</div>
<div class="col"><button type="submit" class="btn btn-success">➕ Añadir</button></div>
</div>
</form>
<div class="table-responsive">
<table class="table table-striped table-bordered">
<thead class="thead-dark">
<tr>
<th>ID Solicitud</th>
<th>Solicitud</th>
<th>URL NVS</th>
<th>Petición</th>
<th>ID Moda</th>
<th>URL Moda</th>
<th>Horas Totales</th>
<th>Fecha Inicio</th>
<th>Fecha Fin</th>
<th>Completada</th>
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

@app.route("/crear_solicitud", methods=["POST"])
def crear_solicitud():
   data = {
       "solicitud": request.form.get("solicitud"),
       "url_nvs": request.form.get("url_nvs"),
       "peticion": request.form.get("peticion"),
       "id_moda": request.form.get("id_moda"),
       "url_moda": request.form.get("url_moda"),
       "horas_totales": float(request.form.get("horas_totales") or 0),
       "fecha_inicio": request.form.get("fecha_inicio"),
       "fecha_fin": request.form.get("fecha_fin"),
       "completada": request.form.get("completada") == "true"
   }
   try:
       supabase.table("solicitudes").insert(data).execute()
       print("✅ Solicitud creada correctamente:", data)
   except Exception as e:
       print("❌ Error al crear solicitud:", e)
   return redirect(url_for("ver_solicitudes"))

@app.route("/editar_solicitud/<int:id_solicitud>", methods=["GET", "POST"])
def editar_solicitud(id_solicitud):
   if request.method == "POST":
       data = {
           "solicitud": request.form.get("solicitud"),
           "url_nvs": request.form.get("url_nvs"),
           "peticion": request.form.get("peticion"),
           "id_moda": request.form.get("id_moda"),
           "url_moda": request.form.get("url_moda"),
           "horas_totales": float(request.form.get("horas_totales") or 0),
           "fecha_inicio": request.form.get("fecha_inicio"),
           "fecha_fin": request.form.get("fecha_fin"),
           "completada": request.form.get("completada") == "true"
       }
       try:
           supabase.table("solicitudes").update(data).eq("id_solicitud", id_solicitud).execute()
           print(f"✏️ Solicitud {id_solicitud} actualizada correctamente")
       except Exception as e:
           print("❌ Error al actualizar solicitud:", e)
       return redirect(url_for("ver_solicitudes"))
   response = supabase.table("solicitudes").select("*").eq("id_solicitud", id_solicitud).single().execute()
   solicitud = response.data
   if not solicitud:
       return f"<h3>No se encontró la solicitud con ID {id_solicitud}</h3>"
   return render_template_string("""
<html>
<head>
<title>Editar Solicitud</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-5">
<h2>Editar Solicitud</h2>
<form method="POST">
<input type="text" name="solicitud" value="{{ solicitud['solicitud'] }}" class="form-control mb-2" required>
<input type="text" name="url_nvs" value="{{ solicitud['url_nvs'] }}" class="form-control mb-2">
<input type="text" name="peticion" value="{{ solicitud['peticion'] }}" class="form-control mb-2">
<input type="text" name="id_moda" value="{{ solicitud['id_moda'] }}" class="form-control mb-2">
<input type="text" name="url_moda" value="{{ solicitud['url_moda'] }}" class="form-control mb-2">
<input type="number" step="0.1" name="horas_totales" value="{{ solicitud['horas_totales'] }}" class="form-control mb-2">
<input type="date" name="fecha_inicio" value="{{ solicitud['fecha_inicio'] }}" class="form-control mb-2">
<input type="date" name="fecha_fin" value="{{ solicitud['fecha_fin'] }}" class="form-control mb-2">
<select name="completada" class="form-control mb-3">
<option value="false" {% if not solicitud['completada'] %}selected{% endif %}>❌ No Completada</option>
<option value="true" {% if solicitud['completada'] %}selected{% endif %}>✅ Completada</option>
</select>
<button type="submit" class="btn btn-primary">💾 Guardar Cambios</button>
<a href="{{ url_for('ver_solicitudes') }}" class="btn btn-secondary">Cancelar</a>
</form>
</body>
</html>
   """, solicitud=solicitud)

@app.route("/eliminar_solicitud/<int:id_solicitud>")
def eliminar_solicitud(id_solicitud):
   try:
       supabase.table("solicitudes").delete().eq("id_solicitud", id_solicitud).execute()
       print(f"🗑️ Solicitud {id_solicitud} eliminada correctamente")
   except Exception as e:
       print("❌ Error al eliminar solicitud:", e)
   return redirect(url_for("ver_solicitudes"))

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
 