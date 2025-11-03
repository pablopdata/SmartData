from flask import Blueprint, render_template_string, request, redirect, url_for

from supabase import create_client, Client

import os

# Configura tu conexión a Supabase

SUPABASE_URL = os.environ.get("SUPABASE_URL")

SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

solicitudes_bp = Blueprint("solicitudes", __name__, url_prefix="/solicitudes")

# --------------------- HTML CON TABLA Y BOOTSTRAP ---------------------

html_template = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Solicitudes</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>

        body {

            background-color: #f8f9fa;

        }

        .table-container {

            width: 100%;

            overflow-x: auto;

        }

        table {

            min-width: 1200px;

            border-collapse: collapse;

            background-color: white;

        }

        th, td {

            white-space: nowrap;

            text-align: center;

            vertical-align: middle;

        }

        thead th {

            background-color: #007bff;

            color: white;

            position: sticky;

            top: 0;

            z-index: 2;

        }

        .container {

            margin-top: 40px;

        }
</style>
</head>
<body>
<div class="container">
<h2 class="mb-4 text-center">Solicitudes</h2>
<a href="{{ url_for('solicitudes.crear_solicitud') }}" class="btn btn-success mb-3">➕ Nueva Solicitud</a>
<div class="table-container shadow-sm p-3 bg-body rounded">
<table class="table table-bordered table-striped table-hover">
<thead>
<tr>
<th>ID</th>
<th>Tarea</th>
<th>URL NVS</th>
<th>Petición</th>
<th>ID Moda</th>
<th>URL Moda</th>
<th>Horas Totales</th>
<th>Fecha Inicio</th>
<th>Fecha Fin</th>
<th>Persona</th>
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

"""

# --------------------- RUTAS ---------------------

@solicitudes_bp.route("/ver_solicitudes")

def ver_solicitudes():

    # Obtenemos todas las solicitudes

    solicitudes = supabase.table("solicitudes").select("*").execute().data

    personas = supabase.table("personas").select("id, nombre").execute().data

    personas_dict = {p["id"]: p["nombre"] for p in personas}

    # Construimos las filas HTML

    table_rows = "".join(

        f"""
<tr>
<td>{row.get('id','')}</td>
<td>{row.get('tarea','')}</td>
<td>{row.get('url_nvs','')}</td>
<td>{row.get('peticion','')}</td>
<td>{row.get('id_moda','')}</td>
<td>{row.get('url_moda','')}</td>
<td>{row.get('horas_totales','')}</td>
<td>{row.get('fecha_inicio','')}</td>
<td>{row.get('fecha_fin','')}</td>
<td>{personas_dict.get(row.get('persona_id'), '—')}</td>
<td>{'✅' if row.get('completada') else '❌'}</td>
<td>
<a href="{url_for('solicitudes.editar_solicitud', id=row.get('id'))}" class="btn btn-warning btn-sm">✏️</a>
<a href="{url_for('solicitudes.eliminar_solicitud', id=row.get('id'))}" class="btn btn-danger btn-sm">🗑️</a>
</td>
</tr>

        """

        for row in solicitudes

    )

    return render_template_string(html_template, table_rows=table_rows)


@solicitudes_bp.route("/crear_solicitud", methods=["GET", "POST"])

def crear_solicitud():

    if request.method == "POST":

        data = {

            "tarea": request.form.get("tarea"),

            "url_nvs": request.form.get("url_nvs"),

            "peticion": request.form.get("peticion"),

            "id_moda": request.form.get("id_moda"),

            "url_moda": request.form.get("url_moda"),

            "horas_totales": request.form.get("horas_totales"),

            "fecha_inicio": request.form.get("fecha_inicio"),

            "fecha_fin": request.form.get("fecha_fin"),

            "persona_id": request.form.get("persona_id"),

            "completada": bool(request.form.get("completada")),

        }

        supabase.table("solicitudes").insert(data).execute()

        return redirect(url_for("solicitudes.ver_solicitudes"))

    personas = supabase.table("personas").select("id, nombre").execute().data

    form_html = """
<div class="container mt-4">
<h3>Nueva Solicitud</h3>
<form method="post">
<div class="mb-3"><label>Tarea</label><input class="form-control" name="tarea"></div>
<div class="mb-3"><label>URL NVS</label><input class="form-control" name="url_nvs"></div>
<div class="mb-3"><label>Petición</label><input class="form-control" name="peticion"></div>
<div class="mb-3"><label>ID Moda</label><input class="form-control" name="id_moda"></div>
<div class="mb-3"><label>URL Moda</label><input class="form-control" name="url_moda"></div>
<div class="mb-3"><label>Horas Totales</label><input class="form-control" name="horas_totales"></div>
<div class="mb-3"><label>Fecha Inicio</label><input type="date" class="form-control" name="fecha_inicio"></div>
<div class="mb-3"><label>Fecha Fin</label><input type="date" class="form-control" name="fecha_fin"></div>
<div class="mb-3">
<label>Persona</label>
<select class="form-select" name="persona_id">

                    {% for persona in personas %}
<option value="{{ persona.id }}">{{ persona.nombre }}</option>

                    {% endfor %}
</select>
</div>
<div class="form-check mb-3">
<input class="form-check-input" type="checkbox" name="completada" id="completada">
<label class="form-check-label" for="completada">Completada</label>
</div>
<button class="btn btn-primary" type="submit">Guardar</button>
<a href="{{ url_for('solicitudes.ver_solicitudes') }}" class="btn btn-secondary">Cancelar</a>
</form>
</div>

    """

    return render_template_string(form_html, personas=personas)


@solicitudes_bp.route("/editar/<int:id>", methods=["GET", "POST"])

def editar_solicitud(id):

    if request.method == "POST":

        data = {

            "tarea": request.form.get("tarea"),

            "url_nvs": request.form.get("url_nvs"),

            "peticion": request.form.get("peticion"),

            "id_moda": request.form.get("id_moda"),

            "url_moda": request.form.get("url_moda"),

            "horas_totales": request.form.get("horas_totales"),

            "fecha_inicio": request.form.get("fecha_inicio"),

            "fecha_fin": request.form.get("fecha_fin"),

            "persona_id": request.form.get("persona_id"),

            "completada": bool(request.form.get("completada")),

        }

        supabase.table("solicitudes").update(data).eq("id", id).execute()

        return redirect(url_for("solicitudes.ver_solicitudes"))

    solicitud = supabase.table("solicitudes").select("*").eq("id", id).execute().data[0]

    personas = supabase.table("personas").select("id, nombre").execute().data

    form_html = """
<div class="container mt-4">
<h3>Editar Solicitud</h3>
<form method="post">
<div class="mb-3"><label>Tarea</label><input class="form-control" name="tarea" value="{{ solicitud.tarea }}"></div>
<div class="mb-3"><label>URL NVS</label><input class="form-control" name="url_nvs" value="{{ solicitud.url_nvs }}"></div>
<div class="mb-3"><label>Petición</label><input class="form-control" name="peticion" value="{{ solicitud.peticion }}"></div>
<div class="mb-3"><label>ID Moda</label><input class="form-control" name="id_moda" value="{{ solicitud.id_moda }}"></div>
<div class="mb-3"><label>URL Moda</label><input class="form-control" name="url_moda" value="{{ solicitud.url_moda }}"></div>
<div class="mb-3"><label>Horas Totales</label><input class="form-control" name="horas_totales" value="{{ solicitud.horas_totales }}"></div>
<div class="mb-3"><label>Fecha Inicio</label><input type="date" class="form-control" name="fecha_inicio" value="{{ solicitud.fecha_inicio }}"></div>
<div class="mb-3"><label>Fecha Fin</label><input type="date" class="form-control" name="fecha_fin" value="{{ solicitud.fecha_fin }}"></div>
<div class="mb-3">
<label>Persona</label>
<select class="form-select" name="persona_id">

                    {% for persona in personas %}
<option value="{{ persona.id }}" {% if solicitud.persona_id == persona.id %}selected{% endif %}>{{ persona.nombre }}</option>

                    {% endfor %}
</select>
</div>
<div class="form-check mb-3">
<input class="form-check-input" type="checkbox" name="completada" id="completada" {% if solicitud.completada %}checked{% endif %}>
<label class="form-check-label" for="completada">Completada</label>
</div>
<button class="btn btn-primary" type="submit">Guardar cambios</button>
<a href="{{ url_for('solicitudes.ver_solicitudes') }}" class="btn btn-secondary">Cancelar</a>
</form>
</div>

    """

    return render_template_string(form_html, solicitud=solicitud, personas=personas)


@solicitudes_bp.route("/eliminar/<int:id>")

def eliminar_solicitud(id):

    supabase.table("solicitudes").delete().eq("id", id).execute()

    return redirect(url_for("solicitudes.ver_solicitudes"))
 