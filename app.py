from flask import Flask, render_template_string, Response
import matplotlib.pyplot as plt
import io
app = Flask(__name__)
@app.route("/")
def index():
   # HTML con tabla a la izquierda y gráfico de tarta a la derecha
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
<tr><td>1</td><td>Implementar login</td><td>4</td></tr>
<tr><td>2</td><td>Revisión de código</td><td>2</td></tr>
<tr><td>3</td><td>Documentación</td><td>3</td></tr>
<tr><td>4</td><td>Reunión cliente</td><td>1</td></tr>
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
<!-- Bootstrap JS -->
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.2/dist/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
   """)
@app.route("/plot.png")
def plot_png():
   # Datos del gráfico de tarta
   horas_imputadas = 10
   horas_totales = 16
   restantes = horas_totales - horas_imputadas
   labels = ['Horas Imputadas', 'Horas Restantes']
   sizes = [horas_imputadas, restantes]
   colors = ['#007bff', '#cccccc']
   fig, ax = plt.subplots()
   ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
   ax.axis('equal')  # Tarta circular
   plt.title("Distribución de Horas")
   output = io.BytesIO()
   fig.savefig(output, format="png", bbox_inches='tight')
   plt.close(fig)
   output.seek(0)
   return Response(output.getvalue(), mimetype="image/png")
if __name__ == "__main__":
   app.run(debug=True)