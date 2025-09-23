from flask import Flask, render_template_string, Response
import matplotlib.pyplot as plt
import io
import base64
app = Flask(__name__)
# Ruta principal
@app.route("/")
def index():
   # HTML mejorado con Bootstrap y barra de navegación
   return render_template_string("""
<html>
<head>
<title>Flask + Matplotlib</title>
<!-- Bootstrap CDN -->
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
<style>
               body {
                   font-family: 'Arial', sans-serif;
                   background-color: #f4f4f9;
               }
               .container {
                   margin-top: 50px;
               }
               .navbar {
                   margin-bottom: 30px;
               }
               h1 {
                   color: #333;
                   text-align: center;
               }
               .btn-custom {
                   background-color: #007bff;
                   color: white;
               }
               .btn-custom:hover {
                   background-color: #0056b3;
               }
</style>
</head>
<body>
<!-- Barra de navegación -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
<a class="navbar-brand" href="#">Flask + Matplotlib para inteligentes smartdateros</a>
<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
<span class="navbar-toggler-icon"></span>
</button>
<div class="collapse navbar-collapse" id="navbarNav">
<ul class="navbar-nav ml-auto">
<li class="nav-item active">
<a class="nav-link" href="/">Inicio</a>
</li>
<li class="nav-item">
<a class="nav-link" href="#">Acerca de</a>
</li>
<li class="nav-item">
<a class="nav-link" href="#">Contacto</a>
</li>
</ul>
</div>
</nav>
<div class="container">
<h1>Gráfica de MatPlotlib</h1>
<!-- Imagen del gráfico -->
<div class="text-center">
<img src="{{ url_for('plot_png') }}" alt="Gráfico" class="img-fluid" style="max-width: 80%;">
</div>
<!-- Botón para recargar el gráfico -->
<div class="text-center mt-4">
<a href="/" class="btn btn-custom btn-lg">Recargar Gráfico</a>
</div>
</div>
<!-- Scripts de Bootstrap -->
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.2/dist/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
   """)
# Ruta para el gráfico
@app.route("/plot.png")
def plot_png():
   # Crear gráfico
   fig, ax = plt.subplots()
   ax.plot([1, 2, 3, 4], [10, 20, 25, 30], marker="o")
   ax.set_title("Ejemplo con Matplotlib")
   ax.set_xlabel("Eje X")
   ax.set_ylabel("Eje Y")
   # Guardar en memoria
   output = io.BytesIO()
   fig.savefig(output, format="png")
   plt.close(fig)
   output.seek(0)
   return Response(output.getvalue(), mimetype="image/png")
if __name__ == "__main__":
   app.run(debug=True)