from flask import Flask, render_template_string, Response
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Ruta principal
@app.route("/")
def index():
    # HTML simple con un gráfico embebido
    return render_template_string("""
    <html>
        <head>
            <title>Flask + Matplotlib</title>
        </head>
        <body>
            <h1>Gráfico generado con Matplotlib</h1>
            <img src="{{ url_for('plot_png') }}" alt="Gráfico">
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
