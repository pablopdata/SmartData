from flask import Flask, render_template_string, Response
from supabase import create_client
import matplotlib.pyplot as plt
import io
import os

app = Flask(__name__)
# Configuración de Supabase
SUPABASE_URL = os.getenv("https://bxgpbkimoqyzfnehgnhh.supabase.co")
SUPABASE_KEY = os.getenv("process.env.SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
@app.route("/")
def index():
   try:
       # Obtener datos desde Supabase
       response = supabase.table("imputaciones").select("*").execute()
       imputaciones = response.data
       if not imputaciones:
           return "No se encontraron datos en la base de datos."
       # Construir HTML de la tabla
       tabla_html = ""
       for item in imputaciones:
           tabla_html += f"<tr><td>{item['id']}</td><td>{item['peticion']}</td><td>{item['horas']}</td></tr>"
       # Calcular horas para el gráfico
       horas_imputadas = sum(item['horas'] for item in imputaciones)
       horas_totales = 16  # Puedes cambiar esto según tu lógica
       restantes = horas_totales - horas_imputadas
       return render_template_string(f"""
<html>
<head>
<title>Imputaciones Smart Data</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
<style>
               body {{ font-family: 'Arial', sans-serif; background-color: #f4f4f9; }}
               .container {{ margin-top: 50px; }}
               h1 {{ color: #333; text-align: center; margin-bottom: 40px; }}
               .table-container {{ max-height: 400px; overflow-y: auto; }}
               .img-fluid {{ max-height: 400px; }}
</style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
<a class="navbar-brand" href="#">IMPUTACIONES SMART DATA</a>
</nav>
<div class="container">
<h1>Resumen de Imputaciones</h1>
<div class="row">
<div class="col-md-6">
<div class="table-container">
<table class="table table-striped table-bordered">
<thead class="thead-dark">
<tr><th>ID</th><th>Petición</th><th>Horas</th></tr>
</thead>
<tbody>
                                   {tabla_html}
</tbody>
</table>
</div>
</div>
<div class="col-md-6 text-center">
<img src="{{ url_for('plot_png') }}" alt="Gráfico de Tarta" class="img-fluid">
</div>
</div>
</div>
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.2/dist/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
       """)
   except Exception as e:
       return f"Error al conectar con la base de datos: {str(e)}"
@app.route("/plot.png")
def plot_png():
   try:
       # Obtener datos desde Supabase
       response = supabase.table("imputaciones").select("*").execute()
       imputaciones = response.data
       horas_imputadas = sum(item['horas'] for item in imputaciones)
       horas_totales = 16
       restantes = horas_totales - horas_imputadas
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
   except Exception as e:
       return f"Error al generar el gráfico: {str(e)}"
if __name__ == "__main__":
   app.run(debug=True)