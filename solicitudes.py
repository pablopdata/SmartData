# solicitudes.py

from flask import Blueprint, request, redirect, url_for, render_template_string

from decimal import Decimal, InvalidOperation

from db import supabase

solicitudes_bp = Blueprint("solicitudes", __name__)

# ---------------- Helpers ----------------

def safe_decimal(value):

    if value is None or value == "":

        return None

    try:

        return Decimal(str(value))

    except (InvalidOperation, ValueError):

        return None

def parse_persona_id(val):

    if val is None or val == "":

        return None

    try:

        return int(val)

    except Exception:

        return val  # podría ser UUID (string)

# ---------------- Ver (lista) con búsqueda y paginación ----------------

@solicitudes_bp.route("/ver_solicitudes")

def ver_solicitudes():

    search = request.args.get("search", "").strip().lower()

    page = int(request.args.get("page", 1))

    per_page = int(request.args.get("per_page", 10))

    # Traer datos

    try:

        solicitudes_all = supabase.table("solicitudes").select("*").order("id_solicitud", desc=True).execute().data or []

    except Exception as e:

        print("❌ Error leyendo solicitudes:", e)

        solicitudes_all = []

    try:

        personas_all = supabase.table("personas").select("id, nombre").execute().data or []

    except Exception as e:

        print("❌ Error leyendo personas:", e)

        personas_all = []

    personas_dict = {p["id"]: p["nombre"] for p in personas_all}

    # Filtrado por búsqueda (en varios campos)

    if search:

        def match(s):

            fields = [

                s.get("tarea", ""),

                s.get("url_nvs", ""),

                s.get("peticion", ""),

                s.get("id_moda", ""),

                s.get("url_moda", ""),

                str(s.get("horas_totales", "")),

                s.get("fecha_inicio", "") or "",

                s.get("fecha_fin", "") or "",

                personas_dict.get(s.get("persona_id"), "")

            ]

            combined = " | ".join([str(f).lower() for f in fields])

            return search in combined

        solicitudes_filtered = [s for s in solicitudes_all if match(s)]

    else:

        solicitudes_filtered = solicitudes_all

    # Paginación

    total = len(solicitudes_filtered)

    total_pages = max(1, (total + per_page - 1) // per_page)

    if page < 1: page = 1

    if page > total_pages: page = total_pages

    start = (page - 1) * per_page

    end = start + per_page

    solicitudes_page = solicitudes_filtered[start:end]

    # Template compacto con buscador, paginación y tabla

    return render_template_string("""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Solicitudes</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>

    body { background:#f7f7f8; padding:18px; }

    .card { padding:12px; }

    .table th, .table td { font-size:0.78rem; padding:6px 8px; white-space:nowrap; text-align:center; }

    .table { min-width:1200px; }

    .table-responsive { overflow-x:auto; }

    .btn-sm { padding:3px 6px; font-size:0.75rem; }

    .search-bar { gap:8px; display:flex; justify-content:center; margin-bottom:12px; }
</style>
</head>
<body>
<div class="container">
<div class="card">
<h4 class="mb-3 text-center">📋 Lista de Solicitudes</h4>
<form method="get" class="search-bar mb-2">
<input type="text" name="search" value="{{ search }}" class="form-control w-50" placeholder="Buscar por tarea, persona, id_moda, etc.">
<select name="per_page" class="form-control" style="max-width:110px;">
<option value="10" {% if per_page==10 %}selected{% endif %}>10</option>
<option value="25" {% if per_page==25 %}selected{% endif %}>25</option>
<option value="50" {% if per_page==50 %}selected{% endif %}>50</option>
</select>
<button class="btn btn-success" type="submit">Buscar</button>
<a href="{{ url_for('solicitudes.ver_solicitudes') }}" class="btn btn-secondary">Reset</a>
<a href="{{ url_for('solicitudes.crear_solicitud') }}" class="btn btn-primary">➕ Nueva</a>
</form>
<div class="table-responsive">
<table class="table table-striped table-bordered">
<thead class="table-dark">
<tr>
<th>ID</th>
<th>Tarea</th>
<th>URL NVS</th>
<th>Petición</th>
<th>ID Moda</th>
<th>URL Moda</th>
<th>Horas</th>
<th>Inicio</th>
<th>Fin</th>
<th>Persona</th>
<th>Completada</th>
<th>Acciones</th>
</tr>
</thead>
<tbody>

            {% if not solicitudes %}
<tr><td colspan="12">No hay datos</td></tr>

            {% else %}

              {% for s in solicitudes %}
<tr>
<td>{{ s.get('id_solicitud') }}</td>
<td>{{ s.get('tarea','') }}</td>
<td>{{ s.get('url_nvs','') }}</td>
<td>{{ s.get('peticion','') }}</td>
<td>{{ s.get('id_moda','') }}</td>
<td>{{ s.get('url_moda','') }}</td>
<td>{{ s.get('horas_totales','') }}</td>
<td>{{ s.get('fecha_inicio','') }}</td>
<td>{{ s.get('fecha_fin','') }}</td>
<td>{{ personas.get(s.get('persona_id'), '—') }}</td>
<td>{{ '✅' if s.get('completada') else '❌' }}</td>
<td>
<a href="{{ url_for('solicitudes.editar_solicitud', id_solicitud=s.get('id_solicitud')) }}" class="btn btn-warning btn-sm">✏️</a>
<a href="{{ url_for('solicitudes.eliminar_solicitud', id_solicitud=s.get('id_solicitud')) }}" class="btn btn-danger btn-sm" onclick="return confirm('Eliminar?')">🗑️</a>
</td>
</tr>

              {% endfor %}

            {% endif %}
</tbody>
</table>
</div>
<!-- Paginación -->
<nav class="mt-2">
<ul class="pagination justify-content-center">

          {% if page > 1 %}
<li class="page-item">
<a class="page-link" href="{{ url_for('solicitudes.ver_solicitudes', page=page-1, per_page=per_page, search=search) }}">« Anterior</a>
</li>

          {% endif %}
<li class="page-item disabled"><span class="page-link">Página {{ page }} / {{ total_pages }}</span></li>

          {% if page < total_pages %}
<li class="page-item">
<a class="page-link" href="{{ url_for('solicitudes.ver_solicitudes', page=page+1, per_page=per_page, search=search) }}">Siguiente »</a>
</li>

          {% endif %}
</ul>
</nav>
</div>
</div>
</body>
</html>

    """,

    solicitudes=solicitudes_page,

    personas=personas_dict,

    search=search,

    page=page,

    per_page=per_page,

    total_pages=total_pages)

# ---------------- Crear ----------------

@solicitudes_bp.route("/crear_solicitud", methods=["GET", "POST"])

def crear_solicitud():

    if request.method == "POST":

        tarea = request.form.get("tarea")

        url_nvs = request.form.get("url_nvs")

        peticion = request.form.get("peticion")

        id_moda = request.form.get("id_moda")

        url_moda = request.form.get("url_moda")

        horas_totales = safe_decimal(request.form.get("horas_totales"))

        fecha_inicio = request.form.get("fecha_inicio") or None

        fecha_fin = request.form.get("fecha_fin") or None

        persona_id = parse_persona_id(request.form.get("persona_id"))

        completada = request.form.get("completada") == "true" or request.form.get("completada") == "on"

        data = {

            "tarea": tarea,

            "url_nvs": url_nvs,

            "peticion": peticion,

            "id_moda": id_moda,

            "url_moda": url_moda,

            "horas_totales": str(horas_totales) if horas_totales is not None else None,

            "fecha_inicio": fecha_inicio,

            "fecha_fin": fecha_fin,

            "persona_id": persona_id,

            "completada": completada

        }

        try:

            res = supabase.table("solicitudes").insert(data).execute()

            print("INSERT result:", res.data)

        except Exception as e:

            print("❌ Error insert:", e)

        return redirect(url_for("solicitudes.ver_solicitudes"))

    # GET -> mostrar formulario

    personas = supabase.table("personas").select("id, nombre").execute().data or []

    return render_template_string("""
<html><head>
<meta charset="utf-8"><title>Nueva solicitud</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body class="p-4">
<div class="container">
<h4>➕ Nueva solicitud</h4>
<form method="post">
<div class="mb-2"><input class="form-control" name="tarea" placeholder="Tarea" required></div>
<div class="mb-2"><input class="form-control" name="url_nvs" placeholder="URL NVS"></div>
<div class="mb-2"><input class="form-control" name="peticion" placeholder="Petición"></div>
<div class="mb-2"><input class="form-control" name="id_moda" placeholder="ID Moda"></div>
<div class="mb-2"><input class="form-control" name="url_moda" placeholder="URL Moda"></div>
<div class="mb-2"><input class="form-control" name="horas_totales" placeholder="Horas totales"></div>
<div class="mb-2"><input type="date" class="form-control" name="fecha_inicio"></div>
<div class="mb-2"><input type="date" class="form-control" name="fecha_fin"></div>
<div class="mb-2">
<select name="persona_id" class="form-control" required>
<option value="">Seleccione persona...</option>

          {% for p in personas %}
<option value="{{ p['id'] }}">{{ p['nombre'] }}</option>

          {% endfor %}
</select>
</div>
<div class="form-check mb-3">
<input class="form-check-input" type="checkbox" id="completada" name="completada">
<label for="completada" class="form-check-label">Completada</label>
</div>
<button class="btn btn-primary" type="submit">Guardar</button>
<a class="btn btn-secondary" href="{{ url_for('solicitudes.ver_solicitudes') }}">Cancelar</a>
</form>
</div>
</body></html>

    """, personas=personas)

# ---------------- Editar ----------------

@solicitudes_bp.route("/editar_solicitud/<int:id_solicitud>", methods=["GET", "POST"])

def editar_solicitud(id_solicitud):

    if request.method == "POST":

        tarea = request.form.get("tarea")

        url_nvs = request.form.get("url_nvs")

        peticion = request.form.get("peticion")

        id_moda = request.form.get("id_moda")

        url_moda = request.form.get("url_moda")

        horas_totales = safe_decimal(request.form.get("horas_totales"))

        fecha_inicio = request.form.get("fecha_inicio") or None

        fecha_fin = request.form.get("fecha_fin") or None

        persona_id = parse_persona_id(request.form.get("persona_id"))

        completada = request.form.get("completada") == "true" or request.form.get("completada") == "on"

        data = {

            "tarea": tarea,

            "url_nvs": url_nvs,

            "peticion": peticion,

            "id_moda": id_moda,

            "url_moda": url_moda,

            "horas_totales": str(horas_totales) if horas_totales is not None else None,

            "fecha_inicio": fecha_inicio,

            "fecha_fin": fecha_fin,

            "persona_id": persona_id,

            "completada": completada

        }

        try:

            res = supabase.table("solicitudes").update(data).eq("id_solicitud", id_solicitud).execute()

            print("UPDATE result:", res.data)

        except Exception as e:

            print("❌ Error update:", e)

        return redirect(url_for("solicitudes.ver_solicitudes"))

    # GET -> cargar solicitud y formulario

    resp = supabase.table("solicitudes").select("*").eq("id_solicitud", id_solicitud).single().execute()

    solicitud = resp.data

    if not solicitud:

        return f"<h3>No encontrada id {id_solicitud}</h3>"

    personas = supabase.table("personas").select("id, nombre").execute().data or []

    return render_template_string("""
<html><head>
<meta charset="utf-8"><title>Editar solicitud</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body class="p-4">
<div class="container">
<h4>✏️ Editar solicitud {{ solicitud['id_solicitud'] }}</h4>
<form method="post">
<div class="mb-2"><input class="form-control" name="tarea" value="{{ solicitud['tarea'] }}"></div>
<div class="mb-2"><input class="form-control" name="url_nvs" value="{{ solicitud['url_nvs'] }}"></div>
<div class="mb-2"><input class="form-control" name="peticion" value="{{ solicitud['peticion'] }}"></div>
<div class="mb-2"><input class="form-control" name="id_moda" value="{{ solicitud['id_moda'] }}"></div>
<div class="mb-2"><input class="form-control" name="url_moda" value="{{ solicitud['url_moda'] }}"></div>
<div class="mb-2"><input class="form-control" name="horas_totales" value="{{ solicitud['horas_totales'] }}"></div>
<div class="mb-2"><input type="date" class="form-control" name="fecha_inicio" value="{{ solicitud['fecha_inicio'] }}"></div>
<div class="mb-2"><input type="date" class="form-control" name="fecha_fin" value="{{ solicitud['fecha_fin'] }}"></div>
<div class="mb-2">
<select name="persona_id" class="form-control" required>
<option value="">Seleccione persona...</option>

          {% for p in personas %}
<option value="{{ p['id'] }}" {% if p['id'] == solicitud.get('persona_id') %}selected{% endif %}>{{ p['nombre'] }}</option>

          {% endfor %}
</select>
</div>
<div class="form-check mb-3">
<input class="form-check-input" type="checkbox" id="completada" name="completada" {% if solicitud.get('completada') %}checked{% endif %}>
<label for="completada" class="form-check-label">Completada</label>
</div>
<button class="btn btn-primary" type="submit">Guardar</button>
<a class="btn btn-secondary" href="{{ url_for('solicitudes.ver_solicitudes') }}">Cancelar</a>
</form>
</div>
</body></html>

    """, solicitud=solicitud, personas=personas)

# ---------------- Eliminar ----------------

@solicitudes_bp.route("/eliminar_solicitud/<int:id_solicitud>")

def eliminar_solicitud(id_solicitud):

    try:

        res = supabase.table("solicitudes").delete().eq("id_solicitud", id_solicitud).execute()

        print("DELETE result:", res.data)

    except Exception as e:

        print("❌ Error delete:", e)

    return redirect(url_for("solicitudes.ver_solicitudes"))
 