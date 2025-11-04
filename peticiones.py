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
<html>
<head>
    <title>Peticiones</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <a class="navbar-brand" href="{{ url_for('index') }}">← Volver</a>
        <span class="navbar-text ml-3 text-white">Gestión de Peticiones</span>
    </nav>
    <div class="container mt-5">
        <h2 class="mb-4">Tabla de Peticiones</h2>
        <form method="POST" action="{{ url_for('peticiones.crear_peticion') }}" class="mb-4">
            <div class="form-row">
                <div class="col">
                    <input type="text" name="nombre_peticion" class="form-control" placeholder="Nombre de la Petición" required>
                </div>
                <div class="col">
                    <button type="submit" class="btn btn-success">➕ Añadir</button>
                </div>
            </div>
        </form>
        <div class="table-responsive">
            <table class="table table-striped table-bordered">
                <thead class="thead-dark">
                    <tr>
                        <th>Nombre de la Petición</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {{ table_rows|safe }}
                </tbody>
            </table>
        </div>
    </div>
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
 