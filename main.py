#Hauptprogramm
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
    conn = get_connection()
    cursor = conn.cursor()
    
    #Fächer abrufen
    cursor.execute("SELECT * FROM subjects")
    subjects_data = cursor.fetchall()
    
    subjects = []
    for subject in subjects_data:
        subject_dict = dict(subject)
        cursor.execute("SELECT * FROM grades WHERE subject_id = ?", (subject["id"],))
        grades = cursor.fetchall()
        subject_dict["grades"] = grades
        
        #Durchschnitt berechnen
        sum_grades = 0
        sum_weights = 0
        for grade in grades:
            weight = 2 if grade["grade_type"] == "Schulaufgabe" else 1
            sum_grades += grade["grade"] * weight
            sum_weights += weight
            
        subject_dict["average"] = round(sum_grades / sum_weights, 2) if sum_weights > 0 else "-"
        subjects.append(subject_dict)
        
    conn.close()
    return render_template("notenübersicht.html", subjects=subjects)

#Fach hinzufügen
@app.route("/subjects/add", methods=["POST"])
def add_subject():
    name = request.form.get("name")
    if name:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
    return redirect(url_for('notenuebersicht'))

#Fach löschen
@app.route("/subjects/delete/<int:id>", methods=["POST"])
def delete_subject(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM grades WHERE subject_id = ?", (id,))
    cursor.execute("DELETE FROM subjects WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('notenuebersicht'))

#Note hinzufügen
@app.route("/grades/add/<int:subject_id>", methods=["POST"])
def add_grade(subject_id):
    grade = request.form.get("grade")
    grade_type = request.form.get("grade_type")
    
    if grade and grade_type:
        weight = 2 if grade_type == "Schulaufgabe" else 1
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO grades (subject_id, grade, weight, grade_type) VALUES (?, ?, ?, ?)",
            (subject_id, int(grade), weight, grade_type)
        )
        conn.commit()
        conn.close()
    return redirect(url_for('notenuebersicht'))

#Note löschen
@app.route("/grades/delete/<int:id>", methods=["POST"])
def delete_grade(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM grades WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('notenuebersicht'))

#Starten des Programms/Applikation
if __name__ == "__main__":
    app.run(debug=True)

