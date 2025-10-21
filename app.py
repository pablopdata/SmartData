from flask import Flask, render_template_string, Response
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

def get_data():
   """Obtiene los datos desde la tabla 'imputaciones' usando la API REST de Supabase"""
   try:
       response = supabase.table("imputaciones").select("*").execute()
       print("📊 Datos obtenidos de Supabase:", response.data)
       return response.data
   except Exception as e:
       print("❌ Error obteniendo datos de Supabase:", e)
       return []

@app.route("/")
def index():
   data = get_data()
   if not data:
       table_rows = "<tr><td colspan='3'>No hay datos disponibles o error de conexión</td></tr>"
   else:
       table_rows = "".join(
           f"<tr><td>{row['id']}</td><td>{row['codigo']}</td><td>{row['horas_totales']}</td></tr>"
           for row in data
       )
   return render_template_string("""
<html>
<head>
<title>Imputaciones Smart Data</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
<style>
body {
   font-family: 'Arial', sans-serif;
   background-color: #f4f4f9;
}
.container { margin-top: 50px; }
h1 { color: #333; text-align: center; margin-bottom: 40px; }
.table-container { max-height: 400px; overflow-y: auto; }
.img-fluid { max-height: 400px; }
.refresh-btn {
   display: block;
   margin: 20px auto;
   background-color: #007bff;
   border: none;
   color: white;
   padding: 10px 25px;
   border-radius: 5px;
   font-size: 16px;
   cursor: pointer;
}
.refresh-btn:hover {
   background-color: #0056b3;
}
</style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
<a class="navbar-brand" href="#">IMPUTACIONES SMART DATA</a>
</nav>
<div class="container">
<h1>Resumen de Imputaciones</h1>
<!-- 🔄 Botón de refresco -->
<button class="refresh-btn" onclick="refreshData()">🔄 Refrescar Datos</button>
<div class="row">
<!-- Tabla a la izquierda -->
<div class="col-md-6">
<div class="table-container">
<table class="table table-striped table-bordered">
<thead class="thead-dark">
<tr><th>id</th><th>codigo</th><th>horas_totales</th></tr>
</thead>
<tbody id="data-table">
{{ table_rows|safe }}
</tbody>
</table>
</div>
</div>
<!-- Gráfico a la derecha -->
<div class="col-md-6 text-center">
<img id="chart" src="{{ url_for('plot_png') }}" alt="Gráfico de Tarta" class="img-fluid">
<p class="mt-3">Horas Imputadas vs Horas Totales</p>
</div>
</div>
</div>
<script>
function refreshData() {
   // Recarga solo la tabla
   fetch(window.location.href)
     .then(response => response.text())
     .then(html => {
         const parser = new DOMParser();
         const doc = parser.parseFromString(html, "text/html");
         document.getElementById("data-table").innerHTML =
             doc.getElementById("data-table").innerHTML;
     });
   // Recarga el gráfico (cambia la URL para evitar caché)
   const chart = document.getElementById("chart");
   chart.src = "/plot.png?" + new Date().getTime();
}
</script>
</body>
</html>
   """, table_rows=table_rows)

@app.route("/plot.png")
def plot_png():
   data = get_data()
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

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))