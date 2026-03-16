#Hauptprogramm
import management
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from db import create_tables, get_connection

app = Flask(__name__)

#Datenbank wird erstellt, falls diese nicht bereits existiert
create_tables()

#Hauptmenü
@app.route("/")
def menu():
    return render_template("menue.html")

#Terminübersicht
@app.route("/termine")
def termine():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments ORDER BY date ASC")
    appointments = cursor.fetchall()
    conn.close()
    
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("termine.html", appointments=appointments, today=today)

#Termin hinzufügen
@app.route("/appointments/add", methods=["POST"])
def add_appointment():
    title = request.form.get("title")
    description = request.form.get("description")
    date = request.form.get("date")
    category = request.form.get("category")

    if date and date < datetime.now().strftime("%Y-%m-%d"):
         return "Fehler: Termine in der Vergangenheit sind nicht erlaubt.", 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (title, description, date, category) VALUES (?, ?, ?, ?)",
        (title, description, date, category)
    )
    conn.commit()
    conn.close()
    
    return redirect(url_for('termine'))

#Termin löschen
@app.route("/appointments/delete/<int:id>", methods=["POST"])
def delete_appointment(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('termine'))

#Notenübersicht
@app.route("/notenuebersicht")
def notenuebersicht():
    return render_template("notenübersicht.html")

#Starten des Programms/Applikation
if __name__ == "__main__":
    app.run(debug=True)

