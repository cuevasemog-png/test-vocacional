from collections import defaultdict
from datetime import datetime
from markupsafe import escape
import random

from flask import Flask, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "clave-secreta-test-vocacional"

# =========================================================
# CONFIGURACIÓN MYSQL (Adaptada para entorno local / XAMPP)
# =========================================================
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:@localhost:3306/test_vocacional2"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================================================
# TEMAS POR ÁREA
# =========================================================
AREA_TEMAS = {
    1: {"icono": "💻", "c1": "#6366f1", "c2": "#8b5cf6"},
    2: {"icono": "🍎", "c1": "#10b981", "c2": "#34d399"},
    3: {"icono": "🚗", "c1": "#f59e0b", "c2": "#f97316"},
    4: {"icono": "⚡", "c1": "#ec4899", "c2": "#a855f7"},
}


def tema_area(area_id):
    return AREA_TEMAS.get(
        area_id,
        {"icono": "🎯", "c1": "#2563eb", "c2": "#3b82f6"},
    )


# =========================================================
# MODELOS
# =========================================================
class AreaVocacional(db.Model):
    __tablename__ = "areas_vocacionales"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Carrera(db.Model):
    __tablename__ = "carreras"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    area_id = db.Column(db.Integer, db.ForeignKey("areas_vocacionales.id"))


class Pregunta(db.Model):
    __tablename__ = "preguntas"
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("areas_vocacionales.id"))


class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100))
    edad = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Respuesta(db.Model):
    __tablename__ = "respuestas"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    pregunta_id = db.Column(db.Integer, db.ForeignKey("preguntas.id"))
    puntuacion = db.Column(db.Integer)


class Resultado(db.Model):
    __tablename__ = "resultados"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    area_id = db.Column(db.Integer, db.ForeignKey("areas_vocacionales.id"))
    puntuacion_total = db.Column(db.Integer)
    porcentaje = db.Column(db.Numeric(5, 2))


# =========================================================
# ESTILOS
# =========================================================
def estilos():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap');

        :root {
            --primary: #6366f1;
            --primary-2: #8b5cf6;
            --accent: #ec4899;
            --secondary: #0f172a;
            --success: #16a34a;
            --background: #f4f7fb;
            --card: rgba(255, 255, 255, .82);
            --text: #172033;
            --muted: #64748b;
            --border: rgba(226, 232, 240, .9);
            --shadow: rgba(79, 70, 229, .18);
        }

        body.dark {
            --secondary: #f1f5f9;
            --background: #070b1a;
            --card: rgba(23, 30, 55, .78);
            --text: #e2e8f0;
            --muted: #94a3b8;
            --border: rgba(71, 85, 130, .5);
            --shadow: rgba(0, 0, 0, .5);
        }

        * { box-sizing: border-box; }
        html { scroll-behavior: smooth; }

        body {
            margin: 0;
            min-height: 100vh;
            color: var(--text);
            font-family: 'Poppins', system-ui, sans-serif;
            background: var(--background);
            overflow-x: hidden;
            transition: background .5s ease, color .4s ease;
        }

        /* ===== FONDO ANIMADO ===== */
        .fondo {
            position: fixed;
            inset: 0;
            z-index: -2;
            overflow: hidden;
            background: linear-gradient(135deg, #eef2ff 0%, #f8fafc 40%, #fdf2f8 100%);
            transition: background .5s ease;
        }

        body.dark .fondo {
            background: linear-gradient(135deg, #050816 0%, #0b1024 50%, #140b22 100%);
        }

        .orbe {
            position: absolute;
            border-radius: 50%;
            filter: blur(70px);
            opacity: .55;
            animation: flotar 18s ease-in-out infinite;
        }
        .orbe.o1 { width: 420px; height: 420px; background: #6366f1; top: -120px; left: -100px; }
        .orbe.o2 { width: 380px; height: 380px; background: #ec4899; bottom: -120px; right: -80px; animation-delay: -6s; }
        .orbe.o3 { width: 320px; height: 320px; background: #10b981; top: 40%; left: 55%; animation-delay: -11s; }

        @keyframes flotar {
            0%, 100% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(60px, -40px) scale(1.15); }
            66% { transform: translate(-40px, 50px) scale(.9); }
        }

        .app-container {
            width: min(calc(100% - 32px), 1050px);
            margin: 0 auto;
            padding: 24px 0 180px;
            position: relative;
        }

        /* ===== BOTÓN TEMA ===== */
        .tema-btn {
            position: fixed;
            top: 18px;
            right: 18px;
            z-index: 500;
            width: 50px;
            height: 50px;
            border: 1px solid var(--border);
            border-radius: 50%;
            background: var(--card);
            backdrop-filter: blur(12px);
            font-size: 1.35rem;
            cursor: pointer;
            box-shadow: 0 8px 24px var(--shadow);
            transition: transform .3s ease, box-shadow .3s ease;
        }
        .tema-btn:hover {
            transform: rotate(25deg) scale(1.12);
            box-shadow: 0 12px 30px var(--shadow);
        }

        /* ===== LOGO ===== */
        .logo-wrapper {
            display: flex;
            justify-content: center;
            margin-bottom: 18px;
        }
        .logo {
            width: clamp(100px, 22vw, 150px);
            height: clamp(100px, 22vw, 150px);
            object-fit: contain;
            border-radius: 24px;
            background: #fff;
            padding: 8px;
            box-shadow: 0 12px 40px var(--shadow);
        }

        /* ===== TARJETAS Y FORMULARIOS ===== */
        .card-custom {
            background: var(--card);
            backdrop-filter: blur(18px);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: clamp(20px, 5vw, 40px);
            box-shadow: 0 24px 60px var(--shadow);
        }
        .form-label { display: block; font-weight: 700; margin-bottom: 8px; font-size: .95rem; }
        .form-control {
            width: 100%;
            min-height: 52px;
            border: 2px solid var(--border);
            border-radius: 16px;
            padding: 12px 16px;
            font-size: 1rem;
            font-family: inherit;
            outline: none;
            background: var(--card);
            color: var(--text);
            transition: border-color .25s ease, box-shadow .25s ease;
        }
        .form-control:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 5px rgba(99, 102, 241, .15);
        }
        .field { margin-bottom: 18px; }

        .btn-main {
            width: 100%;
            min-height: 56px;
            border: 0;
            border-radius: 16px;
            background: linear-gradient(135deg, var(--primary), var(--primary-2));
            color: #fff;
            font-size: 1.05rem;
            font-weight: 800;
            cursor: pointer;
            transition: transform .25s ease, box-shadow .25s ease;
            box-shadow: 0 10px 30px rgba(99, 102, 241, .35);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }
        .btn-main:hover { transform: translateY(-3px); box-shadow: 0 16px 40px rgba(99, 102, 241, .55); color: #fff; }

        .btn-secondary-custom {
            width: 100%;
            min-height: 50px;
            border: 2px solid var(--border);
            border-radius: 16px;
            background: var(--card);
            color: var(--text);
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all .25s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-top: 12px;
        }
        .btn-secondary-custom:hover {
            background: rgba(99, 102, 241, 0.1);
            border-color: var(--primary);
            color: var(--primary);
            transform: translateY(-2px);
        }

        /* ===== OPCIONES Y PREGUNTAS ===== */
        .question { font-size: clamp(1.2rem, 4vw, 1.5rem); font-weight: 800; margin-bottom: 22px; }
        .option {
            display: flex;
            align-items: center;
            gap: 14px;
            width: 100%;
            padding: 15px 18px;
            margin-bottom: 12px;
            border: 2px solid var(--border);
            border-radius: 16px;
            background: var(--card);
            cursor: pointer;
            font-size: 1rem;
            transition: all .2s ease;
        }
        .option:hover {
            border-color: var(--primary);
            background: rgba(99, 102, 241, .07);
            transform: translateX(6px);
        }
        .option input { width: 20px; height: 20px; accent-color: var(--primary); cursor: pointer; }

        /* ===== MASCOTA CAPIBARA ===== */
        .mascota-caja {
            position: fixed;
            right: 24px;
            bottom: 14px;
            z-index: 400;
            pointer-events: none;
            user-select: none;
            filter: drop-shadow(0 14px 26px rgba(0, 0, 0, .22));
        }
        .mascota-img {
            width: 180px;
            height: auto;
            display: block;
            animation: mascotaIdle 4s ease-in-out infinite;
        }
        @keyframes mascotaIdle {
            0%, 100% { transform: translateY(0) rotate(-1.6deg); }
            50% { transform: translateY(-10px) rotate(1.6deg); }
        }
        .capi-globo {
            position: fixed;
            right: 210px;
            bottom: 140px;
            background: #fff;
            color: #1e293b;
            padding: 10px 16px;
            border-radius: 18px;
            font-weight: 800;
            font-size: .9rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            z-index: 401;
        }
        body.dark .capi-globo { background: #1e293b; color: #e2e8f0; }

        @media (max-width: 768px) {
            .mascota-caja { right: 10px; bottom: 5px; }
            .mascota-img { width: 110px; }
            .capi-globo { right: 120px; bottom: 80px; font-size: .75rem; }
        }
    </style>
    """


# =========================================================
# MASCOTA HTML
# =========================================================
def mascota_html():
    return """
    <div class="mascota-caja" id="capi">
        <img src="/static/capibara.png" class="mascota-img" id="mascotaImg" alt="Mascota capibara" onerror="this.style.display='none'">
    </div>
    <div class="capi-globo" id="capiGlobo">¡Hola, a triunfar! 🦫</div>
    """


# =========================================================
# SCRIPTS
# =========================================================
def scripts():
    return """
    <script>
        (function () {
            if (localStorage.getItem("tema") === "oscuro") {
                document.body.classList.add("dark");
            }
        })();

        function alternarTema() {
            document.body.classList.toggle("dark");
            const oscuro = document.body.classList.contains("dark");
            localStorage.setItem("tema", oscuro ? "oscuro" : "claro");
            const btn = document.getElementById("temaBtn");
            if (btn) btn.textContent = oscuro ? "☀️" : "🌙";
        }

        window.addEventListener("DOMContentLoaded", () => {
            const oscuro = document.body.classList.contains("dark");
            const btn = document.getElementById("temaBtn");
            if (btn) btn.textContent = oscuro ? "☀️" : "🌙";
        });
    </script>
    """


# =========================================================
# RUTAS DE LA APLICACIÓN
# =========================================================
@app.route("/")
def index():
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/png" href="{url_for('static', filename='logo.png')}">
        <title>Test Vocacional - ITSJC</title>
        {estilos()}
    </head>
    <body>
        <div class="fondo">
            <div class="orbe o1"></div>
            <div class="orbe o2"></div>
            <div class="orbe o3"></div>
        </div>

        <button class="tema-btn" id="temaBtn" onclick="alternarTema()">🌙</button>

        <div class="app-container">
            <div class="logo-wrapper">
                <img src="{url_for('static', filename='logo.png')}" alt="Logo Instituto" class="logo">
            </div>
            
            <div style="text-align: center; margin-bottom: 24px;">
                <h1 style="font-size: 2.2rem; font-weight: 900; margin-bottom: 8px;">Test Vocacional</h1>
                <p style="color: var(--muted); font-size: 1rem;">Descubre qué carrera se adapta mejor a tus intereses y habilidades.</p>
            </div>

            <div class="card-custom" style="max-width: 500px; margin: 0 auto;">
                <h3 style="margin-bottom: 20px; font-weight: 800; text-align: center;">¡Comencemos!</h3>
                <form method="POST" action="/iniciar_test">
                    <div class="field">
                        <label class="form-label">👤 Nombre completo</label>
                        <input type="text" name="nombre" class="form-control" placeholder="Escribe tu nombre" required>
                    </div>
                    <div class="field">
                        <label class="form-label">✉️ Correo electrónico</label>
                        <input type="email" name="email" class="form-control" placeholder="ejemplo@correo.com" required>
                    </div>
                    <div class="field" style="margin-bottom: 24px;">
                        <label class="form-label">🎂 Edad</label>
                        <input type="number" name="edad" class="form-control" min="14" max="100" placeholder="Tu edad" required>
                    </div>
                    <button type="submit" class="btn-main">Comenzar test 🚀</button>
                </form>
                
                <a href="/dashboard" class="btn-secondary-custom">📊 Ver estadísticas del test</a>
            </div>
        </div>

        {mascota_html()}
        {scripts()}
    </body>
    </html>
    """


@app.route("/dashboard")
def dashboard():
    total_usuarios = Usuario.query.count()

    areas = AreaVocacional.query.all()
    
    # Contar únicamente el área ganadora (mayor porcentaje) por cada usuario
    conteo_area_principal = defaultdict(int)
    for u in Usuario.query.all():
        mejor_resultado = Resultado.query.filter_by(usuario_id=u.id).order_by(Resultado.porcentaje.desc()).first()
        if mejor_resultado:
            conteo_area_principal[mejor_resultado.area_id] += 1

    estadisticas_areas = []
    for area in areas:
        cuenta = conteo_area_principal[area.id]
        datos_a = tema_area(area.id)
        estadisticas_areas.append((area, cuenta, datos_a))

    # Obtener lista de usuarios recientes con sus resultados principales
    usuarios_recientes = Usuario.query.order_by(Usuario.created_at.desc()).limit(10).all()
    registros_tabla = []
    for u in usuarios_recientes:
        mejor_res = Resultado.query.filter_by(usuario_id=u.id).order_by(Resultado.porcentaje.desc()).first()
        carrera_nombre = "Sin definir"
        if mejor_res:
            carrera_obj = Carrera.query.filter_by(area_id=mejor_res.area_id).first()
            if carrera_obj:
                carrera_nombre = carrera_obj.nombre
            else:
                area_obj = db.session.get(AreaVocacional, mejor_res.area_id)
                carrera_nombre = area_obj.nombre if area_obj else "Área General"
        
        registros_tabla.append((u, carrera_nombre, mejor_res.porcentaje if mejor_res else 0))

    areas_html = ""
    for area, cuenta, d in estadisticas_areas:
        areas_html += f"""
        <div style="background: var(--card); border: 1px solid var(--border); border-radius:16px; padding:16px; margin-bottom:12px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h5 style="margin: 0; font-weight: 700;">{d['icono']} {escape(area.nombre)}</h5>
                <p style="margin: 4px 0 0 0; color: var(--muted); font-size: 0.85rem;">{escape(area.descripcion or '')}</p>
            </div>
            <div style="font-size: 1.4rem; font-weight: 900; background: rgba(99,102,241,0.1); padding: 8px 16px; border-radius: 12px; color: var(--primary);">
                {cuenta} <span style="font-size: 0.8rem; font-weight: 600; color: var(--muted);">tests</span>
            </div>
        </div>
        """

    tabla_usuarios_html = ""
    for u, carr, porc in registros_tabla:
        tabla_usuarios_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid var(--border);">{escape(u.nombre)}</td>
            <td style="padding: 12px; border-bottom: 1px solid var(--border); color: var(--muted);">{escape(u.email)}</td>
            <td style="padding: 12px; border-bottom: 1px solid var(--border); font-weight: 600;">{escape(carr)}</td>
            <td style="padding: 12px; border-bottom: 1px solid var(--border); text-align: right; font-weight: 700; color: var(--primary);">{porc:.1f}%</td>
        </tr>
        """

    if not tabla_usuarios_html:
        tabla_usuarios_html = """
        <tr>
            <td colspan="4" style="padding: 20px; text-align: center; color: var(--muted);">Aún no hay registros de estudiantes en el sistema.</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/png" href="{url_for('static', filename='logo.png')}">
        <title>Dashboard Estadístico - ITSJC</title>
        {estilos()}
    </head>
    <body>
        <div class="fondo">
            <div class="orbe o1"></div>
            <div class="orbe o2"></div>
            <div class="orbe o3"></div>
        </div>

        <button class="tema-btn" id="temaBtn" onclick="alternarTema()">🌙</button>

        <div class="app-container" style="max-width: 900px;">
            <div class="logo-wrapper">
                <img src="{url_for('static', filename='logo.png')}" alt="Logo Instituto" class="logo" style="width: 90px; height: 90px;">
            </div>

            <div class="card-custom" style="margin-bottom: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px; margin-bottom: 24px;">
                    <div>
                        <h1 style="font-size: 1.8rem; font-weight: 900; margin: 0;">📊 Panel de Estadísticas (Dashboard)</h1>
                        <p style="color: var(--muted); margin: 4px 0 0 0;">Resumen general de la plataforma del ITSJC</p>
                    </div>
                    <a href="/" class="btn-main" style="width: auto; padding: 10px 20px; min-height: 40px; font-size: 0.9rem;">⬅️ Volver al Inicio</a>
                </div>

                <!-- Tarjeta única de Estudiantes Registrados (ancho completo) -->
                <div style="background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 20px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 28px;">
                    <div style="font-size: 2.5rem; font-weight: 900; color: var(--primary);">{total_usuarios}</div>
                    <div style="color: var(--muted); font-weight: 600; font-size: 1rem; margin-top: 4px;">Estudiantes Registrados</div>
                </div>

                <h3 style="font-weight: 800; font-size: 1.2rem; margin-bottom: 16px;">🎯 Popularidad por Área Vocacional</h3>
                <div style="margin-bottom: 28px;">
                    {areas_html}
                </div>

                <h3 style="font-weight: 800; font-size: 1.2rem; margin-bottom: 16px;">🕒 Últimos Estudiantes Evaluados</h3>
                <div style="overflow-x: auto; background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 10px;">
                    <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.95rem;">
                        <thead>
                            <tr>
                                <th style="padding: 12px; border-bottom: 2px solid var(--border);">Nombre</th>
                                <th style="padding: 12px; border-bottom: 2px solid var(--border);">Correo</th>
                                <th style="padding: 12px; border-bottom: 2px solid var(--border);">Carrera Sugerida</th>
                                <th style="padding: 12px; border-bottom: 2px solid var(--border); text-align: right;">Afinidad</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tabla_usuarios_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        {mascota_html()}
        {scripts()}
    </body>
    </html>
    """


@app.route("/iniciar_test", methods=["POST"])
def iniciar_test():
    preguntas_finales = []
    for area_id in [1, 2, 3, 4]:
        preguntas_area = Pregunta.query.filter_by(area_id=area_id).all()
        if not preguntas_area:
            continue
        random.shuffle(preguntas_area)
        preguntas_seleccionadas = preguntas_area[:5]
        preguntas_finales.extend(preguntas_seleccionadas)

    random.shuffle(preguntas_finales)

    if not preguntas_finales:
        return "No hay preguntas registradas en la base de datos.", 400

    session["preguntas_ids"] = [p.id for p in preguntas_finales]
    session["nombre"] = request.form.get("nombre", "").strip()
    session["email"] = request.form.get("email", "").strip()
    edad_str = request.form.get("edad", "0")
    session["edad"] = int(edad_str) if edad_str.isdigit() else 0
    session["pregunta_actual"] = 0
    session["total_preguntas"] = len(preguntas_finales)
    session["respuestas"] = {}

    return redirect(url_for("test"))


@app.route("/test")
def test():
    if "nombre" not in session or "preguntas_ids" not in session:
        return redirect(url_for("index"))

    preguntas_ids = session["preguntas_ids"]
    pregunta_actual = session.get("pregunta_actual", 0)

    if pregunta_actual >= len(preguntas_ids):
        return redirect(url_for("procesar_resultados"))

    pregunta = db.session.get(Pregunta, preguntas_ids[pregunta_actual])
    if not pregunta:
        return "Error: Pregunta no encontrada.", 404

    progreso = ((pregunta_actual + 1) / len(preguntas_ids)) * 100
    datos_area = tema_area(pregunta.area_id)

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/png" href="{url_for('static', filename='logo.png')}">
        <title>Pregunta {pregunta_actual + 1}</title>
        {estilos()}
    </head>
    <body>
        <div class="fondo">
            <div class="orbe o1"></div>
            <div class="orbe o2"></div>
            <div class="orbe o3"></div>
        </div>

        <button class="tema-btn" id="temaBtn" onclick="alternarTema()">🌙</button>

        <div class="app-container" style="max-width: 700px;">
            <div class="logo-wrapper">
                <img src="{url_for('static', filename='logo.png')}" alt="Logo Instituto" class="logo" style="width: 100px; height: 100px;">
            </div>

            <div class="card-custom">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; color: var(--muted); font-weight: 600; font-size: .9rem;">
                    <span>Pregunta {pregunta_actual + 1} de {len(preguntas_ids)}</span>
                    <span>{progreso:.0f}%</span>
                </div>
                <div style="width: 100%; height: 10px; background: rgba(148,163,184,0.2); border-radius: 10px; margin-bottom: 24px; overflow: hidden;">
                    <div style="width: {progreso}%; height: 100%; background: linear-gradient(90deg, #6366f1, #ec4899);"></div>
                </div>

                <div class="question">
                    <span class="icono-area">{datos_area['icono']}</span> {escape(pregunta.texto)}
                </div>

                <form method="POST" action="/responder">
                    <input type="hidden" name="pregunta_id" value="{pregunta.id}">
                    <label class="option"><input type="radio" name="puntuacion" value="1" required> Nunca</label>
                    <label class="option"><input type="radio" name="puntuacion" value="2"> No</label>
                    <label class="option"><input type="radio" name="puntuacion" value="3"> A veces</label>
                    <label class="option"><input type="radio" name="puntuacion" value="4"> Sí</label>
                    <label class="option"><input type="radio" name="puntuacion" value="5"> Siempre</label>
                    
                    <button type="submit" class="btn-main" style="margin-top: 24px;">Siguiente Pregunta ➡️</button>
                </form>
            </div>
        </div>

        {mascota_html()}
        {scripts()}
    </body>
    </html>
    """


@app.route("/responder", methods=["POST"])
def responder():
    if "respuestas" not in session:
        return redirect(url_for("index"))
    pregunta_id = request.form.get("pregunta_id")
    puntuacion_str = request.form.get("puntuacion")

    if not pregunta_id or not puntuacion_str:
        return "Faltan datos en la respuesta.", 400

    try:
        puntuacion = int(puntuacion_str)
    except ValueError:
        return "Valor inválido.", 400

    respuestas = session.get("respuestas", {})
    respuestas[pregunta_id] = puntuacion
    session["respuestas"] = respuestas
    session["pregunta_actual"] = session.get("pregunta_actual", 0) + 1
    return redirect(url_for("test"))


@app.route("/procesar_resultados")
def procesar_resultados():
    if "respuestas" not in session or not session["respuestas"]:
        return redirect(url_for("index"))

    try:
        nombre = session.get("nombre", "").strip()
        email = session.get("email", "").strip()
        edad = session.get("edad", 0)

        usuario = Usuario(nombre=nombre, email=email, edad=edad)
        db.session.add(usuario)
        db.session.flush()

        puntuaciones_areas = defaultdict(int)
        areas_preguntas = defaultdict(int)

        for pregunta_id, puntuacion in session["respuestas"].items():
            pregunta = db.session.get(Pregunta, int(pregunta_id))
            if pregunta is None:
                continue
            respuesta = Respuesta(usuario_id=usuario.id, pregunta_id=pregunta.id, puntuacion=puntuacion)
            db.session.add(respuesta)
            puntuaciones_areas[pregunta.area_id] += puntuacion
            areas_preguntas[pregunta.area_id] += 1

        resultados = []
        for area_id, puntuacion_total in puntuaciones_areas.items():
            max_puntuacion = areas_preguntas[area_id] * 5
            porcentaje = (puntuacion_total / max_puntuacion) * 100
            resultado = Resultado(usuario_id=usuario.id, area_id=area_id, puntuacion_total=puntuacion_total, porcentaje=porcentaje)
            db.session.add(resultado)
            area = db.session.get(AreaVocacional, area_id)
            carreras = Carrera.query.filter_by(area_id=area_id).all()
            resultados.append((area, porcentaje, carreras))

        resultados.sort(key=lambda x: x[1], reverse=True)
        db.session.commit()

    except Exception as error:
        db.session.rollback()
        return f"Error al procesar resultados: {escape(str(error))}", 500

    area_rec, porc_rec, carreras_rec = resultados[0]
    nombre_carrera_rec = carreras_rec[0].nombre if carreras_rec else area_rec.nombre
    desc_carrera_rec = carreras_rec[0].descripcion if carreras_rec else area_rec.descripcion

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/png" href="{url_for('static', filename='logo.png')}">
        <title>Resultados del Test Vocacional</title>
        {estilos()}
    </head>
    <body>
        <div class="fondo">
            <div class="orbe o1"></div>
            <div class="orbe o2"></div>
            <div class="orbe o3"></div>
        </div>

        <button class="tema-btn" id="temaBtn" onclick="alternarTema()">🌙</button>

        <div class="app-container" style="max-width: 650px;">
            <div class="logo-wrapper">
                <img src="{url_for('static', filename='logo.png')}" alt="Logo Instituto" class="logo" style="width: 100px; height: 100px;">
            </div>

            <div class="card-custom" style="text-align: center;">
                <div style="font-size: 3.5rem; margin-bottom: 10px;">🏆</div>
                <h1 style="font-size: 1.8rem; font-weight: 900; margin-bottom: 6px;">¡Resultados del Test!</h1>
                <p style="color: var(--muted); font-size: 1.1rem; margin-bottom: 24px;">{escape(usuario.nombre)}</p>

                <div style="background: linear-gradient(135deg, var(--primary), var(--primary-2)); color: #fff; padding: 28px; border-radius: 20px; margin-bottom: 24px; box-shadow: 0 12px 30px rgba(99,102,241,0.3);">
                    <h4 style="font-weight: 600; margin-bottom: 8px; font-size: 1rem; opacity: 0.9;">Tu carrera recomendada:</h4>
                    <h2 style="font-size: 2rem; font-weight: 900; margin-bottom: 12px;">{escape(nombre_carrera_rec)}</h2>
                    <span style="background: rgba(255,255,255,0.25); padding: 6px 18px; border-radius: 20px; font-weight: 800; font-size: 1.2rem;">{porc_rec:.1f}% de afinidad</span>
                </div>

                <div style="background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; text-align: left; margin-bottom: 24px;">
                    <h5 style="font-weight: 700; margin-bottom: 8px;">¿En qué consiste?</h5>
                    <p style="color: var(--muted); margin: 0; line-height: 1.6;">{escape(desc_carrera_rec or "")}</p>
                </div>

                <div style="display: flex; gap: 10px; flex-direction: column;">
                    <a href="/reiniciar" class="btn-main" style="text-decoration: none;">🔄 Realizar nuevo test</a>
                    <a href="/dashboard" class="btn-secondary-custom">📊 Ver estadísticas del test</a>
                </div>
            </div>
        </div>

        {mascota_html()}
        {scripts()}
    </body>
    </html>
    """


@app.route("/reiniciar")
def reiniciar():
    session.clear()
    return redirect(url_for("index"))


def init_db():
    with app.app_context():
        try:
            db.create_all()
            print("✅ Tablas creadas correctamente.")
            if AreaVocacional.query.first():
                return

            areas = [
                AreaVocacional(nombre="Informática y Sistemas", descripcion="Aprenderás a programar, crear aplicaciones, manejar bases de datos y administrar redes."),
                AreaVocacional(nombre="Industria Alimentaria", descripcion="Aprenderás a elaborar, conservar y controlar la calidad de los alimentos."),
                AreaVocacional(nombre="Mecánica Automotriz", descripcion="Aprenderás a diagnosticar, reparar y dar mantenimiento a motores y vehículos."),
                AreaVocacional(nombre="Electromecánica", descripcion="Aprenderás a instalar y mantener sistemas eléctricos, máquinas y equipos industriales.")
            ]
            db.session.add_all(areas)
            db.session.commit()

            carreras = [
                Carrera(nombre="Sistemas Informáticos", descripcion="Desarrollo de software, bases de datos y redes informáticas.", area_id=1),
                Carrera(nombre="Industria de Alimentos", descripcion="Transformación y control de calidad de productos alimentarios.", area_id=2),
                Carrera(nombre="Mecánica Automotriz", descripcion="Reparación de motores, sistemas de transmisión y vehículos modernos.", area_id=3),
                Carrera(nombre="Electromecánica", descripcion="Automatización industrial y sistemas eléctricos combinados con mecánica.", area_id=4),
            ]
            db.session.add_all(carreras)
            db.session.commit()

            preguntas = [
                Pregunta(texto="Me gusta descubrir cómo funcionan los programas y aplicaciones", area_id=1),
                Pregunta(texto="Disfruto aprendiendo sobre computadoras, redes y tecnología", area_id=1),
                Pregunta(texto="Me interesa crear o programar mis propias herramientas digitales", area_id=1),
                Pregunta(texto="Prefiero resolver problemas usando la lógica y herramientas informáticas", area_id=1),
                Pregunta(texto="Me atrae el mundo de internet, los sistemas y el tratamiento de información", area_id=1),
                Pregunta(texto="Me interesa saber cómo se elaboran y conservan los alimentos", area_id=2),
                Pregunta(texto="Me llama la atención el proceso de transformación de materias primas en productos", area_id=2),
                Pregunta(texto="Me gustaría trabalhar controlando la calidad y seguridad de los alimentos", area_id=2),
                Pregunta(texto="Tengo curiosidad por conocer los procesos químicos y biológicos de los alimentos", area_id=2),
                Pregunta(texto="Me interesa la parte técnica de producción y procesamiento industrial", area_id=2),
                Pregunta(texto="Me gusta desarmar y armar objetos para entender cómo funcionan", area_id=3),
                Pregunta(texto="Siento curiosidad por saber cómo funcionan los motores y los vehículos", area_id=3),
                Pregunta(texto="Prefiero trabajar con herramientas, piezas y máquinas físicas", area_id=3),
                Pregunta(texto="Me atrae diagnosticar fallas y reparar equipos y automóviles", area_id=3),
                Pregunta(texto="Me interesa aprender el funcionamiento de cada parte de un vehículo", area_id=3),
                Pregunta(texto="Me interesa cómo funcionan la electricidad y los circuitos", area_id=4),
                Pregunta(texto="Disfruto entendiendo cómo se combinan sistemas eléctricos y mecánicos", area_id=4),
                Pregunta(texto="Me gustaría instalar y mantener equipos eléctricos e industriales", area_id=4),
                Pregunta(texto="Siento interés por las máquinas eléctricas, controles y automatización", area_id=4),
                Pregunta(texto="Me atrae trabajar con instalaciones, energía y tecnología industrial", area_id=4),
            ]
            db.session.add_all(preguntas)
            db.session.commit()
            print("✅ Datos iniciales cargados con éxito.")
        except Exception as error:
            db.session.rollback()
            print(f"❌ Error en base de datos: {error}")


if __name__ == "__main__":
    init_db()
    print("🚀 Aplicación iniciada en http://0.0.0.0:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)