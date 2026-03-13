#Hauptprogramm
import management

from flask import Flask, render_template, request, redirect, url_for
from db import create_tables, get_connection

app = Flask(__name__)

create_tables()

@app.route("/")
def menu():
    return render_template("menue.html")


@app.route("/termine")
def termine():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments ORDER BY date ASC")
    appointments = cursor.fetchall()
    conn.close()
    return render_template("termine.html", appointments=appointments)

@app.route("/appointments/add", methods=["POST"])
def add_appointment():
    title = request.form.get("title")
    description = request.form.get("description")
    date = request.form.get("date")
    category = request.form.get("category")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (title, description, date, category) VALUES (?, ?, ?, ?)",
        (title, description, date, category)
    )
    conn.commit()
    conn.close()
    
    return redirect(url_for('termine'))


@app.route("/appointments/delete/<int:id>", methods=["POST"])
def delete_appointment(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('termine'))


@app.route("/notenuebersicht")
def notenuebersicht():
    return render_template("notenübersicht.html")


if __name__ == "__main__":
    app.run(debug=True)

