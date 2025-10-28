from flask import Blueprint, request, redirect, url_for, render_template_string

from db import supabase


# 🔹 Define el Blueprint

solicitudes_bp = Blueprint("solicitudes", __name__)

# ==============================

# 🔹 VER SOLICITUDES

# ==============================

@solicitudes_bp.route("/ver_solicitudes")

def ver_solicitudes():

    try:

        response = supabase.table("solicitudes").select("*").order("id_solicitud", desc=True).execute()

        data = response.data

        print("DEBUG solicitudes:", data)

    except Exception as e:

        print(f"❌ Error obteniendo datos de solicitudes: {e}")

        data = []

    if not data:

        table_rows = "<tr><td colspan='10'>No hay datos disponibles o error de conexión</td></tr>"

    else:

        table_rows = "".join(

            f"<tr>"

            f"<td>{row.get('id_solicitud', '')}</td>"

            f"<td>{row.get('solicitud', '')}</td>"

            f"<td>{row.get('url_nvs', '')}</td>"

            f"<td>{row.get('peticion', '')}</td>"

            f"<td>{row.get('id_moda', '')}</td>"

            f"<td>{row.get('url_moda', '')}</td>"

            f"<td>{row.get('horas_totales', '')}</td>"

            f"<td>{row.get('fecha_inicio', '')}</td>"

            f"<td>{row.get('fecha_fin', '')}</td>"

            f"<td>{'✅' if bool(row.get('completada')) else '❌'}</td>"

            f"<td>"

            f"<a href='{url_for('solicitudes.editar_solicitud', id_solicitud=row.get('id_solicitud'))}' class='btn btn-warning btn-sm'>✏️ Editar</a> "

            f"<a href='{url_for('solicitudes.eliminar_solicitud', id_solicitud=row.get('id_solicitud'))}' class='btn btn-danger btn-sm' onclick='return confirm(\"¿Seguro que quieres eliminar esta solicitud?\")'>🗑️ Eliminar</a>"

            f"</td></tr>"

            for row in data

        )

    return render_template_string("""
<html>
<head>
<title>Solicitudes</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
<a class="navbar-brand" href="{{ url_for('index') }}">← Volver</a>
<span class="navbar-text ml-3 text-white">Gestión de Solicitudes</span>
</nav>
<div class="container mt-5">
<h2 class="mb-4">Tabla de Solicitudes</h2>
<form method="POST" action="{{ url_for('solicitudes.crear_solicitud') }}" class="mb-4">
<div class="form-row">
<div class="col"><input type="text" name="solicitud" class="form-control" placeholder="Solicitud" required></div>
<div class="col"><input type="text" name="url_nvs" class="form-control" placeholder="URL NVS"></div>
<div class="col"><input type="text" name="peticion" class="form-control" placeholder="Petición"></div>
<div class="col"><input type="text" name="id_moda" class="form-control" placeholder="ID Moda"></div>
<div class="col"><input type="text" name="url_moda" class="form-control" placeholder="URL Moda"></div>
</div>
<div class="form-row mt-2">
<div class="col"><input type="number" step="0.1" name="horas_totales" class="form-control" placeholder="Horas Totales"></div>
<div class="col"><input type="date" name="fecha_inicio" class="form-control"></div>
<div class="col"><input type="date" name="fecha_fin" class="form-control"></div>
<div class="col">
<select name="completada" class="form-control">
<option value="false">❌ No Completada</option>
<option value="true">✅ Completada</option>
</select>
</div>
<div class="col"><button type="submit" class="btn btn-success">➕ Añadir</button></div>
</div>
</form>
<div class="table-responsive">
<table class="table table-striped table-bordered">
<thead class="thead-dark">
<tr>
<th>ID Solicitud</th>
<th>Solicitud</th>
<th>URL NVS</th>
<th>Petición</th>
<th>ID Moda</th>
<th>URL Moda</th>
<th>Horas Totales</th>
<th>Fecha Inicio</th>
<th>Fecha Fin</th>
<th>Completada</th>
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

# 🔹 CREAR SOLICITUD

# ==============================

@solicitudes_bp.route("/crear_solicitud", methods=["POST"])

def crear_solicitud():

    data = {

        "solicitud": request.form.get("solicitud"),

        "url_nvs": request.form.get("url_nvs"),

        "peticion": request.form.get("peticion"),

        "id_moda": request.form.get("id_moda"),

        "url_moda": request.form.get("url_moda"),

        "horas_totales": float(request.form.get("horas_totales") or 0),

        "fecha_inicio": request.form.get("fecha_inicio"),

        "fecha_fin": request.form.get("fecha_fin"),

        "completada": request.form.get("completada") == "true"

    }

    try:

        supabase.table("solicitudes").insert(data).execute()

        print("✅ Solicitud creada correctamente:", data)

    except Exception as e:

        print("❌ Error al crear solicitud:", e)

    return redirect(url_for("solicitudes.ver_solicitudes"))

# ==============================

# 🔹 EDITAR SOLICITUD

# ==============================

@solicitudes_bp.route("/editar_solicitud/<int:id_solicitud>", methods=["GET", "POST"])

def editar_solicitud(id_solicitud):

    if request.method == "POST":

        data = {

            "solicitud": request.form.get("solicitud"),

            "url_nvs": request.form.get("url_nvs"),

            "peticion": request.form.get("peticion"),

            "id_moda": request.form.get("id_moda"),

            "url_moda": request.form.get("url_moda"),

            "horas_totales": float(request.form.get("horas_totales") or 0),

            "fecha_inicio": request.form.get("fecha_inicio"),

            "fecha_fin": request.form.get("fecha_fin"),

            "completada": request.form.get("completada") == "true"

        }

        try:

            supabase.table("solicitudes").update(data).eq("id_solicitud", id_solicitud).execute()

            print(f"✏️ Solicitud {id_solicitud} actualizada correctamente")

        except Exception as e:

            print("❌ Error al actualizar solicitud:", e)

        return redirect(url_for("solicitudes.ver_solicitudes"))

    response = supabase.table("solicitudes").select("*").eq("id_solicitud", id_solicitud).single().execute()

    solicitud = response.data

    if not solicitud:

        return f"<h3>No se encontró la solicitud con ID {id_solicitud}</h3>"

    return render_template_string("""
<html>
<head>
<title>Editar Solicitud</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-5">
<h2>Editar Solicitud</h2>
<form method="POST">
<input type="text" name="solicitud" value="{{ solicitud['solicitud'] }}" class="form-control mb-2" required>
<input type="text" name="url_nvs" value="{{ solicitud['url_nvs'] }}" class="form-control mb-2">
<input type="text" name="peticion" value="{{ solicitud['peticion'] }}" class="form-control mb-2">
<input type="text" name="id_moda" value="{{ solicitud['id_moda'] }}" class="form-control mb-2">
<input type="text" name="url_moda" value="{{ solicitud['url_moda'] }}" class="form-control mb-2">
<input type="number" step="0.1" name="horas_totales" value="{{ solicitud['horas_totales'] }}" class="form-control mb-2">
<input type="date" name="fecha_inicio" value="{{ solicitud['fecha_inicio'] }}" class="form-control mb-2">
<input type="date" name="fecha_fin" value="{{ solicitud['fecha_fin'] }}" class="form-control mb-2">
<select name="completada" class="form-control mb-3">
<option value="false" {% if not solicitud['completada'] %}selected{% endif %}>❌ No Completada</option>
<option value="true" {% if solicitud['completada'] %}selected{% endif %}>✅ Completada</option>
</select>
<button type="submit" class="btn btn-primary">💾 Guardar Cambios</button>
<a href="{{ url_for('solicitudes.ver_solicitudes') }}" class="btn btn-secondary">Cancelar</a>
</form>
</body>
</html>

    """, solicitud=solicitud)

# ==============================

# 🔹 ELIMINAR SOLICITUD

# ==============================

@solicitudes_bp.route("/eliminar_solicitud/<int:id_solicitud>")

def eliminar_solicitud(id_solicitud):

    try:

        supabase.table("solicitudes").delete().eq("id_solicitud", id_solicitud).execute()

        print(f"🗑️ Solicitud {id_solicitud} eliminada correctamente")

    except Exception as e:

        print("❌ Error al eliminar solicitud:", e)

    return redirect(url_for("solicitudes.ver_solicitudes"))
 