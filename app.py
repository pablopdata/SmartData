from flask import Flask, render_template_string, Response
import matplotlib.pyplot as plt
import io
import os
import psycopg2
from psycopg2.extras import RealDictCursor
app = Flask(__name__)
# ⚙️ Carga la URL de conexión desde una variable de entorno
DB_URL = os.getenv("SUPABASE_DB_URL")
def get_data():
   """Obtiene los datos desde la tabla 'imputaciones' de Supabase"""
   try:
       conn = psycopg2.connect(DB_URL, sslmode="require", cursor_factory=RealDictCursor)
       cur = conn.cursor()
       cur.execute("SELECT * FROM imputaciones ORDER BY id;")
       data = cur.fetchall()
       cur.close()
       conn.close()
       return data
   except Exception as e:
       print("❌ Error conectando a la base de datos:", e)
       return []
@app.route("/")
def index():
   data = get_data()
   if not data:
       table_rows = "<tr><td colspan='3'>No hay datos disponibles o error de conexión</td></tr>"
   else:
       table_rows = "".join(
           f"<tr><td>{row['id']}</td><td>{row['peticion']}</td><td>{row['horas']}</td></tr>" for row in data
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
<th>id</th>
<th>codigo</th>
<th>horas_totales</th>
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
   # Flask usará el puerto proporcionado por Render automáticamente
   app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))