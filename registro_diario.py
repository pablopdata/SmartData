from flask import Blueprint, render_template_string, request, redirect, url_for

from db import supabase

registro_bp = Blueprint("registro", __name__)

# 🔹 Mostrar tabla de registro diario

@registro_bp.route("/ver_tabla")

def ver_tabla():

    try:

        response = supabase.table("registro_diario").select("*").order("fecha", desc=True).execute()

        data = response.data

    except Exception as e:

        print(f"❌ Error obteniendo datos: {e}")

        data = []

    table_rows = "".join(

        f"<tr>"

        f"<td>{row.get('fecha','')}</td><td>{row.get('tarea','')}</td><td>{row.get('persona','')}</td>"

        f"<td>{row.get('horas','')}</td><td>{row.get('peticion','')}</td>"

        f"<td>{row.get('porcentaje_real','')}</td><td>{row.get('porcentaje_nvs','')}</td>"

        f"<td>"

        f"<a href='/editar_registro/{row.get('id')}' class='btn btn-warning btn-sm'>✏️</a> "

        f"<a href='/eliminar_registro/{row.get('id')}' class='btn btn-danger btn-sm'>🗑️</a>"

        f"</td></tr>"

        for row in data

    ) if data else "<tr><td colspan='8'>No hay datos disponibles</td></tr>"

    return render_template_string("""
<html>
<head>
<title>Registro Diario</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
<a class="navbar-brand" href="{{ url_for('imputaciones.index') }}">← Volver</a>
</nav>
<div class="container mt-5">
<h2>Tabla registro_diario</h2>
<form method="POST" action="/crear_registro" class="mb-4">
<div class="form-row">
<div class="col"><input type="date" name="fecha" class="form-control" required></div>
<div class="col"><input type="text" name="tarea" placeholder="Tarea" class="form-control" required></div>
<div class="col"><input type="text" name="persona" placeholder="Persona" class="form-control" required></div>
<div class="col"><input type="number" step="0.1" name="horas" placeholder="Horas" class="form-control" required></div>
<div class="col"><input type="text" name="peticion" placeholder="Petición" class="form-control"></div>
<div class="col"><input type="number" name="porcentaje_real" placeholder="% Real" class="form-control"></div>
<div class="col"><input type="number" name="porcentaje_nvs" placeholder="% NVS" class="form-control"></div>
<div class="col"><button type="submit" class="btn btn-success">➕ Añadir</button></div>
</div></form>
<table class="table table-striped table-bordered"><thead class="thead-dark">
<tr><th>Fecha</th><th>Tarea</th><th>Persona</th><th>Horas</th><th>Petición</th><th>% Real</th><th>% NVS</th><th>Acciones</th></tr>
</thead><tbody>{{ table_rows|safe }}</tbody></table></div></body></html>

""", table_rows=table_rows)

# 🔹 Crear nuevo registro

@registro_bp.route("/crear_registro", methods=["POST"])

def crear_registro():

    data = {

        "fecha": request.form.get("fecha"),

        "tarea": request.form.get("tarea"),

        "persona": request.form.get("persona"),

        "horas": float(request.form.get("horas")),

        "peticion": request.form.get("peticion"),

        "porcentaje_real": request.form.get("porcentaje_real"),

        "porcentaje_nvs": request.form.get("porcentaje_nvs")

    }

    supabase.table("registro_diario").insert(data).execute()

    return redirect(url_for("registro.ver_tabla"))

# 🔹 Editar registro existente

@registro_bp.route("/editar_registro/<int:registro_id>", methods=["GET", "POST"])

def editar_registro(registro_id):

    if request.method == "POST":

        data = {

            "fecha": request.form.get("fecha"),

            "tarea": request.form.get("tarea"),

            "persona": request.form.get("persona"),

            "horas": float(request.form.get("horas")),

            "peticion": request.form.get("peticion"),

            "porcentaje_real": request.form.get("porcentaje_real"),

            "porcentaje_nvs": request.form.get("porcentaje_nvs")

        }

        supabase.table("registro_diario").update(data).eq("id", registro_id).execute()

        return redirect(url_for("registro.ver_tabla"))

    registro = supabase.table("registro_diario").select("*").eq("id", registro_id).single().execute().data

    return render_template_string("""
<html>
<head><title>Editar Registro</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-5">
<h2>Editar Registro Diario</h2>
<form method="POST">
<input type="date" name="fecha" value="{{ registro['fecha'] }}" class="form-control mb-2" required>
<input type="text" name="tarea" value="{{ registro['tarea'] }}" class="form-control mb-2" required>
<input type="text" name="persona" value="{{ registro['persona'] }}" class="form-control mb-2" required>
<input type="number" step="0.1" name="horas" value="{{ registro['horas'] }}" class="form-control mb-2" required>
<input type="text" name="peticion" value="{{ registro['peticion'] }}" class="form-control mb-2">
<input type="number" name="porcentaje_real" value="{{ registro['porcentaje_real'] }}" class="form-control mb-2">
<input type="number" name="porcentaje_nvs" value="{{ registro['porcentaje_nvs'] }}" class="form-control mb-2">
<button type="submit" class="btn btn-primary">💾 Guardar</button>
<a href="{{ url_for('registro.ver_tabla') }}" class="btn btn-secondary">Cancelar</a>
</form>
</body></html>

""", registro=registro)

# 🔹 Eliminar registro

@registro_bp.route("/eliminar_registro/<int:registro_id>")

def eliminar_registro(registro_id):

    supabase.table("registro_diario").delete().eq("id", registro_id).execute()

    return redirect(url_for("registro.ver_tabla"))
 