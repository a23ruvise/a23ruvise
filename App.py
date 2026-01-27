from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecreto"

# =======================
# BASE DE DATOS EXTERNA
# =======================
DB_FOLDER = "/sqlite3-db"
DB = os.path.join(DB_FOLDER, "liga.db")

# Crear carpeta si no existe (solo por seguridad en local)
os.makedirs(DB_FOLDER, exist_ok=True)

# =======================
# UTILIDADES BASE DE DATOS
# =======================
def conexion():
    return sqlite3.connect(DB)

def init_db():
    with conexion() as con:
        cur = con.cursor()
        # Tabla equipos
        cur.execute('''
            CREATE TABLE IF NOT EXISTS equipos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                ciudad TEXT,
                estadio TEXT,
                entrenador TEXT,
                fundacion INTEGER
            )
        ''')

        # Tabla jugadores con nuevo campo estado_forma
        cur.execute('''
            CREATE TABLE IF NOT EXISTS jugadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                posicion TEXT,
                numero INTEGER,
                nacionalidad TEXT,
                equipo_id INTEGER NOT NULL,
                estado_forma INTEGER DEFAULT 0,
                FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE
            )
        ''')
        con.commit()

init_db()

# =======================
# RUTAS
# =======================

@app.route("/")
def home():
    con = conexion()
    cur = con.cursor()
    cur.execute("SELECT * FROM equipos")
    equipos = cur.fetchall()

    equipos_jugadores = []
    for e in equipos:
        cur.execute("SELECT * FROM jugadores WHERE equipo_id=?", (e[0],))
        jugadores = cur.fetchall()
        equipos_jugadores.append((e, jugadores))

    return render_template("home.html", equipos_jugadores=equipos_jugadores)

@app.route("/equipo/<int:id_equipo>")
def mostrar_equipo(id_equipo):
    con = conexion()
    cur = con.cursor()
    cur.execute("SELECT * FROM equipos WHERE id=?", (id_equipo,))
    equipo = cur.fetchone()

    cur.execute("SELECT * FROM jugadores WHERE equipo_id=?", (id_equipo,))
    jugadores = cur.fetchall()
    return render_template("equipo.html", equipo=equipo, jugadores=jugadores)

@app.route("/jugador/<int:id_jugador>")
def mostrar_jugador(id_jugador):
    con = conexion()
    cur = con.cursor()
    cur.execute("SELECT * FROM jugadores WHERE id=?", (id_jugador,))
    jugador = cur.fetchone()
    return render_template("jugador.html", jugador=jugador)

# =======================
# CRUD Equipos
# =======================

@app.route("/nuevo_equipo", methods=["GET", "POST"])
def nuevo_equipo():
    if request.method == "POST":
        nombre = request.form["nombre"]
        ciudad = request.form["ciudad"]
        estadio = request.form["estadio"]
        entrenador = request.form["entrenador"]
        fundacion = request.form["fundacion"]

        con = conexion()
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO equipos (nombre, ciudad, estadio, entrenador, fundacion) VALUES (?,?,?,?,?)",
                        (nombre, ciudad, estadio, entrenador, fundacion))
            con.commit()
            flash("Equipo creado correctamente", "success")
            return redirect(url_for("home"))
        except sqlite3.IntegrityError:
            flash("El nombre del equipo ya existe", "danger")
    return render_template("nuevo_equipo.html")

@app.route("/editar_equipo/<int:id_equipo>", methods=["GET", "POST"])
def editar_equipo(id_equipo):
    con = conexion()
    cur = con.cursor()
    if request.method == "POST":
        nombre = request.form["nombre"]
        ciudad = request.form["ciudad"]
        estadio = request.form["estadio"]
        entrenador = request.form["entrenador"]
        fundacion = request.form["fundacion"]
        try:
            cur.execute("""
                UPDATE equipos SET nombre=?, ciudad=?, estadio=?, entrenador=?, fundacion=? WHERE id=?
            """, (nombre, ciudad, estadio, entrenador, fundacion, id_equipo))
            con.commit()
            flash("Equipo actualizado correctamente", "success")
            return redirect(url_for("home"))
        except sqlite3.IntegrityError:
            flash("El nombre del equipo ya existe", "danger")

    cur.execute("SELECT * FROM equipos WHERE id=?", (id_equipo,))
    equipo = cur.fetchone()
    return render_template("editar_equipo.html", equipo=equipo)

@app.route("/eliminar_equipo/<int:id_equipo>")
def eliminar_equipo(id_equipo):
    con = conexion()
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM equipos WHERE id=?", (id_equipo,))
        con.commit()
        flash("Equipo eliminado correctamente", "success")
    except sqlite3.IntegrityError:
        flash("No se puede eliminar este equipo porque tiene jugadores asociados", "danger")
    return redirect(url_for("home"))

# =======================
# CRUD Jugadores
# =======================

@app.route("/nuevo_jugador", methods=["GET", "POST"])
def nuevo_jugador():
    con = conexion()
    cur = con.cursor()
    cur.execute("SELECT id, nombre FROM equipos")
    equipos = cur.fetchall()

    if request.method == "POST":
        nombre = request.form["nombre"]
        posicion = request.form["posicion"]
        numero = request.form["numero"]
        nacionalidad = request.form["nacionalidad"]
        equipo_id = request.form["equipo_id"]
        estado_forma = request.form["estado_forma"]

        cur.execute("""
            INSERT INTO jugadores (nombre, posicion, numero, nacionalidad, equipo_id, estado_forma) 
            VALUES (?,?,?,?,?,?)
        """, (nombre, posicion, numero, nacionalidad, equipo_id, estado_forma))
        con.commit()
        flash("Jugador creado correctamente", "success")
        return redirect(url_for("home"))

    return render_template("nuevo_jugador.html", equipos=equipos)

@app.route("/editar_jugador/<int:id_jugador>", methods=["GET", "POST"])
def editar_jugador(id_jugador):
    con = conexion()
    cur = con.cursor()
    cur.execute("SELECT * FROM jugadores WHERE id=?", (id_jugador,))
    jugador = cur.fetchone()

    cur.execute("SELECT id, nombre FROM equipos")
    equipos = cur.fetchall()

    if request.method == "POST":
        nombre = request.form["nombre"]
        posicion = request.form["posicion"]
        numero = request.form["numero"]
        nacionalidad = request.form["nacionalidad"]
        equipo_id = request.form["equipo_id"]
        estado_forma = request.form["estado_forma"]

        cur.execute("""
            UPDATE jugadores SET nombre=?, posicion=?, numero=?, nacionalidad=?, equipo_id=?, estado_forma=? WHERE id=?
        """, (nombre, posicion, numero, nacionalidad, equipo_id, estado_forma, id_jugador))
        con.commit()
        flash("Jugador actualizado correctamente", "success")
        return redirect(url_for("home"))

    return render_template("editar_jugador.html", jugador=jugador, equipos=equipos)

@app.route("/eliminar_jugador/<int:id_jugador>")
def eliminar_jugador(id_jugador):
    con = conexion()
    cur = con.cursor()
    cur.execute("DELETE FROM jugadores WHERE id=?", (id_jugador,))
    con.commit()
    flash("Jugador eliminado correctamente", "success")
    return redirect(url_for("home"))

# =======================
# Ranking por estado de forma
# =======================

@app.route("/ranking/<int:estado>")
def ranking_estado(estado):
    con = conexion()
    cur = con.cursor()
    cur.execute("""
        SELECT j.id, j.nombre, j.numero, j.equipo_id, e.nombre 
        FROM jugadores j 
        JOIN equipos e ON j.equipo_id = e.id
        WHERE estado_forma=?
    """, (estado,))
    jugadores = cur.fetchall()
    return render_template("ranking.html", jugadores=jugadores, estado=estado)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
