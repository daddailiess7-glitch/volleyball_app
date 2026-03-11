from flask import Flask, render_template, request, redirect, send_file
import sqlite3
from datetime import datetime
import pandas as pd

app = Flask(__name__)

# تهيئة قاعدة البيانات
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY, name TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS attendance(id INTEGER PRIMARY KEY, player TEXT, date TEXT, status TEXT)")
    conn.commit()
    conn.close()

init_db()

# صفحة تسجيل الحضور للاعبين
@app.route("/")
def home():
    conn = sqlite3.connect("database.db")
    players = conn.execute("SELECT name FROM players").fetchall()
    conn.close()
    return render_template("index.html", players=players)

# تسجيل حضور/غياب
@app.route("/attendance", methods=["POST"])
def attendance():
    player = request.form["player"]
    status = request.form["status"]
    date = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect("database.db")
    conn.execute("INSERT INTO attendance (player,date,status) VALUES (?,?,?)",
                 (player,date,status))
    conn.commit()
    conn.close()
    return redirect("/")

# لوحة تحكم المدرب
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("database.db")
    attendance = conn.execute("SELECT * FROM attendance ORDER BY date DESC").fetchall()
    players = conn.execute("SELECT name FROM players").fetchall()
    conn.close()
    return render_template("dashboard.html", attendance=attendance, players=players)

# إضافة لاعب جديد
@app.route("/add_player", methods=["POST"])
def add_player():
    name = request.form["name"]
    conn = sqlite3.connect("database.db")
    conn.execute("INSERT INTO players (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

# تصدير Excel
@app.route("/export")
def export():
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT * FROM attendance", conn)
    conn.close()
    file = "attendance.xlsx"
    df.to_excel(file,index=False)
    return send_file(file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")