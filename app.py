from flask import Flask, render_template_string, Response, url_for
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# Ruta principal
@app.route("/")
def index():
    # HTML con Bootstrap y barra de navegación
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Flask + Matplotlib</title>
            <!-- Bootstrap 5 CDN -->
            https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css
        </head>
        <body>
            <!-- Barra de navegación Bootstrap -->
            <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
                <div class="container-fluid">
                    #Mi App Flask</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item">
                                {{ url_for(Inicio</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href                     </li>
                            <li class="nav-item">
                                #Contacto</a>
                            </li>
                            <li class="nav-item">
                                <button class="btn btn-light ms-2" type="button">Botón</button>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
            <div class="container">
                <h1 class="mb-4">Gráfico generado con Matplotlib</h1>
                <img src="{{ url_for('plot_png') }}" alt="Gráfico" class="img-fluidnal, para navbar responsive) -->
            <script src="https://cdn.jsdelivrstrap@5.3.2/dist/js/bootstrap.bundle.min.js
        </body>
    </html>
    """)

# Ruta para el gráfico
@app.route("/plot.png")
def plot_png():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [10, 20, 25, 30], marker="o")
    ax.set_title("Ejemplo con Matplotlib")
    ax.set_xlabel("Eje X")
    ax.set_ylabel("Eje Y")

    output = io.BytesIO()
    fig.savefig(output, format="png")
    plt.close(fig)
    output.seek(0)
    return Response(output.getvalue(), mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
