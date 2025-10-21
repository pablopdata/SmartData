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
       response = supabase.table("imputaciones").select("id, peticion, horas").execute()
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
           f"<tr><td>{row['id']}</td><td>{row['peticion']}</td><td>{row['horas']}</td></tr>"
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
.container {
   margin-top: 50px;
}
h1 {
   color: #333;
   text-align: center;
   margin-bottom: 40px;
}
.table-container {
   max-height: 400px;
   overflow-y: auto;
}
.img-fluid {
   max-height: 400px;
}
</style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
<a class="navbar-brand" href="#">IMPUTACIONES SMART DATA</a>
</nav>
<div class="container">
<h1>Resumen de Imputaciones</h1>
<div class="row">
<!-- Tabla a la izquierda -->
<div class="col-md-6">
<div class="table-container">
<table class="table table-striped table-bordered">
<thead class="thead-dark">
<tr>
<th>ID</th>
<th>Petición</th>
<th>Horas</th>
</tr>
</thead>
<tbody>
{{ table_rows|safe }}
</tbody>
</table>
</div>
</div>
<!-- Gráfico a la derecha -->
<div class="col-md-6 text-center">
<img src="{{ url_for('plot_png') }}" alt="Gráfico de Tarta" class="img-fluid">
<p class="mt-3">Horas Imputadas vs Horas Totales</p>
</div>
</div>
</div>
</body>
</html>
   """, table_rows=table_rows)
@app.route("/plot.png")
def plot_png():
   data = get_data()
   horas_imputadas = sum(d['horas'] for d in data) if data else 0
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