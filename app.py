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
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Imputaciones Smart Data</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/cssin.css
        <style>
            body { font-family: 'Arial', sans-serif; background-color: #f4f4f9; }
            .container { margin-top: 50px; }
            h1 { color: #333; text-align: center; margin-bottom: 40px; }
            .table-container { max-height: 400px; overflow-y: auto; }
            .img-fluid { max-height: 400px; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            #IMPUTACIONES SMART DATA</a>
        </nav>
        <div class="container">
            <h1>Resumen de Imputaciones</h1>
            <div class="row">
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
                <div class="col-md-6 text-center">
                    {{ url_for(
                    <p class="mt-3">Horas Imputadas vs Horas Totales</p>
                </div>
            </div>
        </div>
        https://code.jquery.com/jquery-3.5.1.slim.min.js</script>
        <script src.jsdelivr.net/npm/@popperjs/core@2.5.2/dist/umd/popper.min.js</script>
        <script src="https://stackpath.com/bootstrap/4.5.2/js/bootstrap.min.js</script>
    </body>
    </html>
    """, table_rows=table_rows)

@app.route("/plot.png")
def plot_png():
    data = get_data()
    horas_imputadas = sum(d.get('horas_totales', 0) for d in data) if data else 0
    horas_totales = 16  # Puedes ajustar este valor según tu lógica
    restantes = max(horas_totales - horas_imputadas, 0)
    labels = ['Horas Imputadas', 'Horas Restantes']
    sizes = [horas_imputadas, restantes]
    colors = ['#007bff', '#cccccc']

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')
    plt("Distribución de Horas")

    output = io.BytesIO()
    fig.savefig(output, format="png", bbox_inches='tight')
    plt.close(fig)
    output.seek(0)
    return Response(output.getvalue(), mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))