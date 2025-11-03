from flask import Blueprint, request, redirect, url_for, render_template_string

from db import supabase

peticiones_bp = Blueprint("peticiones", __name__)

# ==============================

# 🔹 VER Peticiones

# ==============================

@peticiones_bp.route("/ver_peticiones")

def ver_peticiones():

    try:

        peticiones_res = supabase.table("peticiones").select("*").order("id_peticion", desc=True).execute()

        peticiones = peticiones_res.data or []

    except Exception as e:

        print(f"❌ Error obteniendo datos: {e}")

        peticiones = []

    # Generar filas de la tabla

    if not peticiones:

        table_rows = "<tr><td colspan='11'>No hay datos disponibles</td></tr>"

    else:

        table_rows = "".join(

            f"<tr>"

            f"<td>{row.get('nombre_peticion', '')}</td>"

            f"<td>"

            f"<a href='{url_for('peticiones.editar_peticion', id_peticion=row.get('id_peticion'))}' class='btn btn-warning btn-sm'>✏️</a> "

            f"<a href='{url_for('peticiones.eliminar_peticion', id_peticion=row.get('id_peticion'))}' class='btn btn-danger btn-sm' onclick='return confirm(\"¿Seguro que quieres eliminar esta petición?\")'>🗑️</a>"

            f"</td></tr>"

            for row in peticiones

        )

    return render_template_string("""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Peticiones • SmartData</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background: #f5f7fb; }
    .hero { background: linear-gradient(90deg,#4f46e5 0%,#06b6d4 100%); color: white; }
    .card-table { box-shadow: 0 6px 18px rgba(15,23,42,0.08); }
    .table td, .table th { vertical-align: middle; }
    .brand-back { text-decoration: none; color: rgba(255,255,255,0.9); }
    @media (max-width:576px){ .actions-col { width: 1px; white-space: nowrap; } }
  </style>
</head>
<body>
  <nav class="navbar navbar-dark hero">
    <div class="container">
      <a class="brand-back d-flex align-items-center" href="{{ url_for('index') }}">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-left" viewBox="0 0 16 16">
          <path fill-rule="evenodd" d="M15 8a.5.5 0 0 1-.5.5H3.707l3.147 3.146a.5.5 0 0 1-.708.708l-4-4a.5.5 0 0 1 0-.708l4-4a.5.5 0 1 1 .708.708L3.707 7.5H14.5A.5.5 0 0 1 15 8z"/>
        </svg>
        <span class="ms-2 fw-semibold">Volver</span>
      </a>
      <div class="text-end">
        <h5 class="mb-0">Gestión de Peticiones</h5>
        <small class="opacity-75">Administra, edita y elimina peticiones</small>
      </div>
    </div>
  </nav>

  <main class="container my-5">
    <div class="row g-4">
      <div class="col-12">
        <div class="card p-3 card-table">
          <div class="d-flex align-items-center justify-content-between mb-3 gap-2 flex-wrap">
            <div>
              <h4 class="mb-0">Peticiones</h4>
              <small class="text-muted">Lista ordenada por fecha (más recientes arriba)</small>
            </div>

            <div class="d-flex gap-2 align-items-center">
              <input id="searchInput" type="search" class="form-control form-control-sm" placeholder="Buscar petición...">
              <form method="POST" action="{{ url_for('peticiones.crear_peticion') }}" class="d-flex ms-2">
                <input name="nombre_peticion" type="text" class="form-control form-control-sm" placeholder="Nueva petición" required>
                <button class="btn btn-success btn-sm ms-2" type="submit">➕ Añadir</button>
              </form>
            </div>
          </div>

          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>Nombre</th>
                  <th class="text-center actions-col">Acciones</th>
                </tr>
              </thead>
              <tbody id="peticionesTable">
                {{ table_rows|safe }}
              </tbody>
            </table>
          </div>

          <div class="mt-2 text-muted small">
            Mostrando <strong id="countLabel">--</strong> peticiones.
          </div>
        </div>
      </div>
    </div>
  </main>

  <footer class="text-center py-3 text-muted small">
    SmartData • Sistema de gestión — UI mejorada
  </footer>

  <script>
    // Simple client-side search & counter
    const searchInput = document.getElementById('searchInput');
    const table = document.getElementById('peticionesTable');
    const countLabel = document.getElementById('countLabel');

    function updateCount() {
      const visible = Array.from(table.querySelectorAll('tr')).filter(r => r.style.display !== 'none').length;
      countLabel.textContent = visible;
    }

    function filterRows() {
      const q = searchInput.value.trim().toLowerCase();
      const rows = table.querySelectorAll('tr');
      rows.forEach(r => {
        const text = r.innerText.toLowerCase();
        r.style.display = text.includes(q) ? '' : 'none';
      });
      updateCount();
    }

    // initial count
    window.addEventListener('load', () => {
      updateCount();
    });

    searchInput.addEventListener('input', filterRows);
  </script>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""", table_rows=table_rows)

# ==============================

# 🔹 CREAR peticion

# ==============================

@peticiones_bp.route("/crear_peticion", methods=["POST"])

def crear_peticion():

    data = {

        "nombre_peticion": request.form.get("nombre_peticion")

    }

    try:

        supabase.table("peticiones").insert(data).execute()

        print("✅ Petición creada correctamente:", data)

    except Exception as e:

        print("❌ Error al crear peticion:", e)

    return redirect(url_for("peticiones.ver_peticiones"))
 


# ==============================

# 🔹 EDITAR PETICIÓN

# ==============================

@peticiones_bp.route("/editar_peticion/<int:id_peticion>", methods=["GET", "POST"])

def editar_peticion(id_peticion):

    if request.method == "POST":

        data = {

            "nombre_peticion": request.form.get("nombre_peticion")

        }

        try:

            supabase.table("peticiones").update(data).eq("id_peticion", id_peticion).execute()

            print(f"✏️ Petición {id_peticion} actualizada")

        except Exception as e:

            print("❌ Error actualizando peticion:", e)

        return redirect(url_for("peticiones.ver_peticiones"))

    response = supabase.table("peticiones").select("*").eq("id_peticion", id_peticion).single().execute()

    peticion = response.data

    return render_template_string("""
<html>
<head>
    <title>Editar Petición</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-5">
    <h2>Editar Petición</h2>
    <form method="POST">
        <input type="text" name="nombre_peticion" value="{{ peticion['nombre_peticion'] }}" class="form-control mb-2">
        <button type="submit" class="btn btn-primary">💾 Guardar</button>
        <a href="{{ url_for('peticiones.ver_peticiones') }}" class="btn btn-secondary">Cancelar</a>
    </form>
</body>
</html>

""", peticion=peticion)


# ==============================

# 🔹 ELIMINAR PETICIÓN

# ==============================

@peticiones_bp.route("/eliminar_peticion/<int:id_peticion>")

def eliminar_peticion(id_peticion):

    try:

        supabase.table("peticiones").delete().eq("id_peticion", id_peticion).execute()

        print(f"🗑️ Petición {id_peticion} eliminada")

    except Exception as e:

        print("❌ Error eliminando peticion:", e)

    return redirect(url_for("peticiones.ver_peticiones"))
 