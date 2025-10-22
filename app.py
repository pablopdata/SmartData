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

# 🔹 Nueva página: REGISTRO_DIARIO
@app.route("/ver_tabla")
def ver_tabla():
   data = get_data("registro_diario")  # Asegúrate del nombre exacto de tu tabla en Supabase
   if not data:
       table_rows = "<tr><td colspan='7'>No hay datos disponibles o error de conexión</td></tr>"
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