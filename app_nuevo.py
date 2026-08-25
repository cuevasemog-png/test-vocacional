from collections import defaultdict
from datetime import datetime
from markupsafe import escape
import random

from flask import Flask, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "mi-clave-secreta-test-vocacional-2024"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:@localhost:3306/test_vocacional2"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ===== MODELOS =====
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
    area_id = db.Column(db.Integer, db.ForeignKey("areas_vocacionales.id"), nullable=False)


class Pregunta(db.Model):
    __tablename__ = "preguntas"
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("areas_vocacionales.id"), nullable=False)


class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Respuesta(db.Model):
    __tablename__ = "respuestas"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey("preguntas.id"), nullable=False)
    puntuacion = db.Column(db.Integer, nullable=False)


class Resultado(db.Model):
    __tablename__ = "resultados"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("areas_vocacionales.id"), nullable=False)
    puntuacion_total = db.Column(db.Integer, nullable=False)
    porcentaje = db.Column(db.Numeric(5, 2), nullable=False)


# ===== RUTAS =====
@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Vocacional - Instituto</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Roboto, sans-serif;
            }
            .logo-container { text-align: center; margin-bottom: 20px; }
            .logo { max-width: 200px; height: auto; }
            .card {
                background: #ffffff;
                border-radius: 20px;
                box-shadow: 0 15px 40px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            .form-label { font-weight: 600; color: #2c3e50; }
            .form-control {
                border-radius: 12px;
                border: 2px solid #e0e6ed;
                padding: 10px 15px;
                transition: all 0.3s ease;
            }
            .form-control:focus {
                border-color: #007bff;
                box-shadow: 0 0 0 0.2rem rgba(0,123,255,0.25);
            }
            .btn-custom {
                background: linear-gradient(90deg, #ff6b35, #f7931e);
                color: white;
                font-weight: 600;
                border-radius: 12px;
                padding: 12px;
                border: none;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .btn-custom:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(255,107,53,0.35);
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="d-flex justify-content-center align-items-center min-vh-100 py-5">
            <div class="card" style="width: 420px;">
                <div class="card-body px-4 pb-4 pt-4">
                    <!-- ✅ LOGO DENTRO DEL CUADRO -->
                    <div class="logo-container">
                        <img src="/static/logo.png" alt="Logo del Instituto" class="logo">
                    </div>
                    <h1 class="text-center mb-2" style="color: #0f2027; font-weight: 700;">Test Vocacional</h1>
                    <p class="text-center text-muted mb-4">Descubre tu carrera ideal</p>
                    <form method="POST" action="/iniciar_test">
                        <div class="mb-3">
                            <label class="form-label">👤 Nombre completo</label>
                            <input type="text" name="nombre" class="form-control" placeholder="Tu nombre" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">✉️ Correo electrónico</label>
                            <input type="email" name="email" class="form-control" placeholder="correo@ejemplo.com" required>
                        </div>
                        <div class="mb-4">
                            <label class="form-label">🎂 Edad</label>
                            <input type="number" name="edad" class="form-control" min="14" max="100" placeholder="Tu edad" required>
                        </div>
                        <button type="submit" class="btn btn-custom w-100">🚀 Comenzar Test</button>
                    </form>
                </div>
            </div>
        </div>
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

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pregunta {pregunta_actual + 1}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Roboto, sans-serif;
                padding: 30px 15px;
            }}
            .logo-small {{ text-align: center; margin-bottom: 15px; }}
            .logo-small img {{ max-width: 140px; }}
            .card {{
                border-radius: 20px;
                box-shadow: 0 15px 40px rgba(0,0,0,0.3);
                border: none;
                overflow: hidden;
            }}
            .card-body {{ padding: 30px; }}
            .progress {{
                height: 28px;
                border-radius: 14px;
                background-color: #e9ecef;
                overflow: hidden;
                margin-bottom: 25px;
            }}
            .progress-bar {{
                background: linear-gradient(90deg, #007bff, #00c6ff);
                font-weight: 600;
            }}
            .pregunta-texto {{
                font-size: 1.25rem;
                color: #1a1a2e;
                font-weight: 600;
                line-height: 1.5;
                margin-bottom: 30px;
            }}
            .form-check-input {{ width: 20px; height: 20px; margin-top: 6px; cursor: pointer; }}
            .form-check-label {{ font-size: 1.05rem; color: #2c3e50; padding-left: 8px; cursor: pointer; }}
            .opcion {{
                background: #f8f9fa;
                border-radius: 12px;
                padding: 12px 15px;
                margin-bottom: 10px;
                transition: background 0.2s ease;
            }}
            .opcion:hover {{ background: #e3f2fd; }}
            .btn-siguiente {{
                background: linear-gradient(90deg, #007bff, #00c6ff);
                color: white;
                font-weight: 600;
                border-radius: 12px;
                padding: 12px;
                border: none;
                transition: transform 0.2s ease;
            }}
            .btn-siguiente:hover {{ transform: translateY(-2px); color: white; }}
        </style>
    </head>
    <body>
        <div class="container" style="max-width: 700px;">
            <div class="card">
                <div class="card-body">
                    <!-- ✅ LOGO DENTRO DEL CUADRO BLANCO -->
                    <div class="logo-small">
                        <img src="/static/logo.png" alt="Logo Instituto">
                    </div>

                    <h4 class="mb-3 text-center" style="color: #0f2027; font-weight: 700;">Pregunta {pregunta_actual + 1} de {len(preguntas_ids)}</h4>
                    <div class="progress">
                        <div class="progress-bar" style="width: {progreso:.1f}%">
                            {progreso:.0f}%
                        </div>
                    </div>
                    <p class="pregunta-texto">{escape(pregunta.texto)}</p>
                    <form method="POST" action="/responder">
                        <input type="hidden" name="pregunta_id" value="{pregunta.id}">
                        <div class="opcion">
                            <input class="form-check-input" type="radio" name="puntuacion" value="1" id="r1" required>
                            <label class="form-check-label" for="r1"> Nunca</label>
                        </div>
                        <div class="opcion">
                            <input class="form-check-input" type="radio" name="puntuacion" value="2" id="r2">
                            <label class="form-check-label" for="r2"> No</label>
                        </div>
                        <div class="opcion">
                            <input class="form-check-input" type="radio" name="puntuacion" value="3" id="r3">
                            <label class="form-check-label" for="r3"> A veces</label>
                        </div>
                        <div class="opcion">
                            <input class="form-check-input" type="radio" name="puntuacion" value="4" id="r4">
                            <label class="form-check-label" for="r4"> Si</label>
                        </div>
                        <div class="opcion">
                            <input class="form-check-input" type="radio" name="puntuacion" value="5" id="r5">
                            <label class="form-check-label" for="r5"> Siempre</label>
                        </div>
                        <button type="submit" class="btn btn-siguiente w-100 mt-4">Siguiente Pregunta ➡️</button>
                    </form>
                </div>
            </div>
        </div>
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
        return "Valor de puntuación inválido.", 400

    if puntuacion not in range(1, 6):
        return "Puntuación fuera del rango permitido (1-5).", 400

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

        if not nombre or not email or edad <= 0:
            return "Faltan datos del usuario. Vuelve a iniciar el test.", 400

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

    todas_areas_html = ""
    posicion_emoji = ["🥇", "🥈", "🥉", "🏅"]
    for idx, (area, porc, carreras) in enumerate(resultados):
        emoji = posicion_emoji[idx] if idx < 4 else "🔹"
        lista_carreras = ", ".join([c.nombre for c in carreras]) if carreras else "Sin carreras registradas"
        todas_areas_html += f"""
        <div style="background:#f8f9fa; border-radius:12px; padding:15px; margin-bottom:10px;">
            <h6 class="mb-2">{emoji} <strong>{escape(area.nombre)}</strong> — {porc:.1f}%</h6>
            <p class="mb-0 text-muted small">{escape(lista_carreras)}</p>
        </div>
        """

    resultados_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resultados del Test Vocacional</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Roboto, sans-serif;
                padding: 30px 15px;
            }}
            .logo-small {{ text-align: center; margin-bottom: 10px; }}
            .logo-small img {{ max-width: 140px; }}
            .card {{
                border-radius: 20px;
                box-shadow: 0 15px 40px rgba(0,0,0,0.3);
                border: none;
                overflow: hidden;
            }}
            .header-result {{
                background: linear-gradient(90deg, #007bff, #00c6ff);
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .recomendada {{
                background: linear-gradient(90deg, #ff6b35, #f7931e);
                color: white;
                padding: 35px 25px;
                border-radius: 16px;
                text-align: center;
                margin: 30px 20px;
                box-shadow: 0 8px 25px rgba(255,107,53,0.35);
            }}
            .porcentaje-box {{
                background: rgba(255,255,255,0.25);
                display: inline-block;
                padding: 10px 25px;
                border-radius: 30px;
                margin-top: 15px;
                font-size: 1.3rem;
                font-weight: 700;
            }}
            .descripcion-carrera {{
                background: #f8f9fa;
                border-radius: 14px;
                padding: 25px;
                margin: 0 20px 30px 20px;
                text-align: center;
            }}
            .otras-areas {{
                margin: 0 20px 30px 20px;
            }}
            .btn-reiniciar {{
                background: linear-gradient(90deg, #28a745, #20c997);
                color: white;
                font-weight: 600;
                border-radius: 12px;
                padding: 12px 30px;
                border: none;
            }}
            .btn-reiniciar:hover {{ color: white; }}
        </style>
    </head>
    <body>
        <div class="container" style="max-width: 600px;">
            <div class="card">
                <!-- ✅ LOGO DENTRO DEL CUADRO CELESTE -->
                <div class="header-result">
                    <div class="logo-small">
                        <img src="/static/logo.png" alt="Logo Instituto">
                    </div>
                    <h2 class="mb-0">🎓 Resultados del Test Vocacional</h2>
                    <p class="mb-0 mt-1 fs-5">— {escape(usuario.nombre)} —</p>
                </div>

                <div class="card-body px-0 py-4">
                    <div class="recomendada">
                        <h4 class="mb-3">🏆 Tu Carrera Recomendada:</h4>
                        <h2 class="display-5 fw-bold">{escape(nombre_carrera_rec)}</h2>
                        <div class="porcentaje-box">{porc_rec:.1f}%</div>
                    </div>

                    <div class="descripcion-carrera">
                        <h5 class="fw-bold text-muted mb-3">¿En qué consiste?</h5>
                        <p class="fs-6">{escape(desc_carrera_rec or "")}</p>
                    </div>

                    <div class="otras-areas">
                        <h5 class="fw-bold text-center mb-3 text-muted">📋 Todas tus áreas</h5>
                        {todas_areas_html}
                    </div>

                    <div class="text-center mt-3 mb-4">
                        <a href="/reiniciar" class="btn btn-reiniciar">🔄 Realizar nuevo test</a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return resultados_html


@app.route("/reiniciar")
def reiniciar():
    session.clear()
    return redirect(url_for("index"))


def init_db():
    with app.app_context():
        try:
            db.create_all()
            print("✅ Tablas creadas.")
            if AreaVocacional.query.first():
                print("ℹ️ Datos existentes detectados, se omite carga inicial.")
                return

            areas = [
                AreaVocacional(nombre="Informática y Sistemas", descripcion="Aprenderás a programar, crear aplicaciones, manejar bases de datos y administrar redes. Desarrollarás soluciones usando tecnología."),
                AreaVocacional(nombre="Industria Alimentaria", descripcion="Aprenderás a elaborar, conservar y controlar la calidad de los alimentos. Conocerás cómo transformar materias primas en productos seguros."),
                AreaVocacional(nombre="Mecánica Automotriz", descripcion="Aprenderás a diagnosticar, reparar y dar mantenimiento a motores y vehículos. Trabajarás con herramientas y piezas mecánicas."),
                AreaVocacional(nombre="Electromecánica", descripcion="Aprenderás a instalar y mantener sistemas eléctricos, máquinas y equipos industriales. Combinarás electricidad con mecánica.")
            ]
            db.session.add_all(areas)
            db.session.commit()

            carreras = [
                Carrera(
                    nombre="Sistemas Informáticos",
                    descripcion="Aprenderás a programar, crear aplicaciones, manejar bases de datos y administrar redes. Desarrollarás soluciones usando tecnología.",
                    area_id=1
                ),
                Carrera(
                    nombre="Industria de Alimentos",
                    descripcion="Aprenderás a elaborar, conservar y controlar la calidad de los alimentos. Conocerás cómo transformar materias primas en productos seguros.",
                    area_id=2
                ),
                Carrera(
                    nombre="Mecánica Automotriz",
                    descripcion="Aprenderás a diagnosticar, reparar y dar mantenimiento a motores y vehículos. Trabajarás con herramientas y piezas mecánicas.",
                    area_id=3
                ),
                Carrera(
                    nombre="Electromecánica",
                    descripcion="Aprenderás a instalar y mantener sistemas eléctricos, máquinas y equipos industriales. Combinarás electricidad con mecánica.",
                    area_id=4
                ),
            ]
            db.session.add_all(carreras)
            db.session.commit()

            preguntas = [
                Pregunta(texto="Me gusta descubrir cómo funcionan los programas y aplicaciones", area_id=1),
                Pregunta(texto="Disfruto aprendiendo sobre computadoras, redes y tecnología", area_id=1),
                Pregunta(texto="Me interesa crear o programar mis propias herramientas digitales", area_id=1),
                Pregunta(texto="Prefiero resolver problemas usando la lógica y herramientas informáticas", area_id=1),
                Pregunta(texto="Me atrae el mundo de internet, los sistemas y el tratamiento de información", area_id=1),
                Pregunta(texto="Me imagino creando aplicaciones que ayuden a las personas", area_id=1),
                Pregunta(texto="Siento curiosidad por saber cómo se protege la información en internet", area_id=1),
                Pregunta(texto="Me interesa saber cómo se elaboran y conservan los alimentos", area_id=2),
                Pregunta(texto="Me llama la atención el proceso de transformación de materias primas en productos", area_id=2),
                Pregunta(texto="Me gustaría trabajar controlando la calidad y seguridad de los alimentos", area_id=2),
                Pregunta(texto="Tengo curiosidad por conocer los procesos químicos y biológicos de los alimentos", area_id=2),
                Pregunta(texto="Me interesa la parte técnica de producción y procesamiento industrial", area_id=2),
                Pregunta(texto="Me atrae investigar cómo mejorar el valor nutricional de los alimentos", area_id=2),
                Pregunta(texto="Me gustaría innovar en nuevas formas de envasar y conservar productos", area_id=2),
                Pregunta(texto="Me gusta desarmar y armar objetos para entender cómo funcionan", area_id=3),
                Pregunta(texto="Siento curiosidad por saber cómo funcionan los motores y los vehículos", area_id=3),
                Pregunta(texto="Prefiero trabajar con herramientas, piezas y máquinas físicas", area_id=3),
                Pregunta(texto="Me atrae diagnosticar fallas y reparar equipos y automóviles", area_id=3),
                Pregunta(texto="Me interesa aprender el funcionamiento de cada parte de un vehículo", area_id=3),
                Pregunta(texto="Me gustaría conocer cómo se diseñan y fabrican los vehículos modernos", area_id=3),
                Pregunta(texto="Disfruto al ver cómo una máquina cobra vida al armarla correctamente", area_id=3),
                Pregunta(texto="Me interesa cómo funcionan la electricidad y los circuitos", area_id=4),
                Pregunta(texto="Disfruto entendiendo cómo se combinan sistemas eléctricos y mecánicos", area_id=4),
                Pregunta(texto="Me gustaría instalar y mantener equipos eléctricos e industriales", area_id=4),
                Pregunta(texto="Siento interés por las máquinas eléctricas, controles y automatización", area_id=4),
                Pregunta(texto="Me atrae trabajar con instalaciones, energía y tecnología industrial", area_id=4),
                Pregunta(texto="Me llama la atención saber cómo funciona la maquinaria de una fábrica", area_id=4),
                Pregunta(texto="Me imagino controlando procesos automáticos usando electricidad", area_id=4),
            ]
            db.session.add_all(preguntas)
            db.session.commit()
            print("✅ Datos cargados.")
        except Exception as error:
            db.session.rollback()
            print(f"❌ Error: {error}")


if __name__ == "__main__":
    init_db()
    print("🚀 Aplicación iniciada en http://0.0.0.0:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)