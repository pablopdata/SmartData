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

def get_data():
    """Obtiene los datos desde la tabla 'imputaciones' usando la API REST de Supabase"""
    try:
        response = supabase.table("imputaciones").select("*").execute()
        print("📊 Datos obtenidos de Supabase:", response.data)
        return response.data
    except Exception as e:
        print("❌ Error obteniendo datos de Supabase:", e)
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Captura datos del formulario
        codigo = request.form.get("codigo")
        horas_totales = int(request.form.get("horas_totales", 0))

        # Inserta en Supabase
        try:
            supabase.table("imputaciones").insert({
                "codigo": codigo,
                "horas_totales": horas_totales
            }).execute()
            print("✅ Registro insertado correctamente")
        except Exception as e:
            print("❌ Error insertando registro:", e)

        return redirect(url_for("index"))

    # Si es GET, muestra los datos
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
        <link href="https://stackpath.bootstrapcdn.com.5.2/css/bootstrap.min.css
        <style>
            body { font-family: 'Arial', sans-serif; background-color: #f4f4f9; }
            .container { margin-top: 50px; }
            h1 { color: #333; text-align: center; margin-bottom: 40px; }
            .table-container { max-height: 400px; overflow-y: auto; }
            .img-fluid { max-height: 400px; }
            .form-section { margin-bottom: 30px; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            #IMPUTACIONES SMART DATA</a>
        </nav>
        <div class="container">
            <h1>Resumen de Imputaciones</h1>

            <!-- Formulario para añadir registros -->
            <div class="form-section">
                <form method="POST" class="form-inline justify-content-center">
                    <input type="text" name="codigo" placeholder="Código" class="form-control mr-2" required>
                    <input type="number" name="horas_totales" placeholder="Horas Totales" class="form-control mr-2" required>
                    <button type="submit" class="btn btn-primary">Añadir</button>
                </form>
            </div>

            <div class="row">
                <!-- Tabla -->
                <div class="col-md-6">
                    <div class="table-container">
                        <table class="table table-striped table-bordered">
                            <thead class="thead-dark">
                                <tr><th>ID</th><th>Código</th><th>Horas Totales</th></tr>
                            </thead>
                            <tbody>
                                {{ table_rows|safe }}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Gráfico -->
                <div class="col-md-6 text-center">
                    {{ url_for(
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