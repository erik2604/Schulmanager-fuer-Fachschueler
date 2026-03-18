#Hauptprogramm
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import create_tables, get_connection

app = Flask(__name__)
app.secret_key = "geheimes_passwort_hier_ändern" # Wichtig für die Session

#Datenbank wird erstellt, falls diese nicht bereits existiert
create_tables()


def calculate_overall_average(cursor, user_id):
    cursor.execute('''
        SELECT grades.grade, grades.weight, grades.grade_type 
        FROM grades 
        JOIN subjects ON grades.subject_id = subjects.id 
        WHERE subjects.user_id = ?
    ''', (user_id,))
    grades = cursor.fetchall()

    sum_grades = 0
    sum_weights = 0

    for grade in grades:
        weight = grade["weight"] if grade["weight"] else (2 if grade["grade_type"] == "Schulaufgabe" else 1)
        sum_grades += grade["grade"] * weight
        sum_weights += weight

    if sum_weights == 0:
        return None

    return round(sum_grades / sum_weights, 2)

#Registrierung (optional zum Anlegen von Usern)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            flash("Benutzername existiert bereits.")
            return redirect(url_for('register'))
            
        hashed_pw = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password, firstname, lastname) VALUES (?, ?, ?, ?)",
            (username, hashed_pw, firstname, lastname)
        )
        conn.commit()
        conn.close()
        flash("Registrierung erfolgreich. Bitte einloggen.")
        return redirect(url_for('login'))
        
    return render_template("register.html")

#Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["firstname"] = user["firstname"]
            return redirect(url_for("menu"))
        else:
            flash("Falscher Benutzername oder Passwort.")
            
    return render_template("login.html")

#Logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("firstname", None)
    return redirect(url_for("login"))

#Hauptmenü
@app.route("/")
def menu():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_connection()
    cursor = conn.cursor()
    overall_average = calculate_overall_average(cursor, session["user_id"])
    conn.close()

    return render_template("menue.html", overall_average=overall_average, firstname=session.get("firstname"))

#Terminübersicht
@app.route("/termine")
def termine():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE user_id = ? ORDER BY date ASC", (session["user_id"],))
    appointments = cursor.fetchall()
    conn.close()
    
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("termine.html", appointments=appointments, today=today)

#Termin hinzufügen
@app.route("/appointments/add", methods=["POST"])
def add_appointment():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    title = request.form.get("title")
    description = request.form.get("description")
    date = request.form.get("date")
    category = request.form.get("category")

    if date and date < datetime.now().strftime("%Y-%m-%d"):
         return "Fehler: Termine in der Vergangenheit sind nicht erlaubt.", 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (title, description, date, category, user_id) VALUES (?, ?, ?, ?, ?)",
        (title, description, date, category, session["user_id"])
    )
    conn.commit()
    conn.close()
    
    return redirect(url_for('termine'))

#Termin löschen
@app.route("/appointments/delete/<int:id>", methods=["POST"])
def delete_appointment(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_connection()
    cursor = conn.cursor()
    # Nur eigene Termine dürfen gelöscht werden
    cursor.execute("DELETE FROM appointments WHERE id = ? AND user_id = ?", (id, session["user_id"]))
    conn.commit()
    conn.close()
    
    return redirect(url_for('termine'))

#Notenübersicht
@app.route("/notenuebersicht")
def notenuebersicht():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_connection()
    cursor = conn.cursor()
    
    #Fächer abrufen
    cursor.execute("SELECT * FROM subjects WHERE user_id = ?", (session["user_id"],))
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
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    name = request.form.get("name")
    if name:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subjects (name, user_id) VALUES (?, ?)", (name, session["user_id"]))
        conn.commit()
        conn.close()
    return redirect(url_for('notenuebersicht'))

#Fach löschen
@app.route("/subjects/delete/<int:id>", methods=["POST"])
def delete_subject(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_connection()
    cursor = conn.cursor()
    # Sicherheitsabfrage: Gehört das Fach dem aktuellen Nutzer?
    cursor.execute("SELECT id FROM subjects WHERE id = ? AND user_id = ?", (id, session["user_id"]))
    if cursor.fetchone():
        cursor.execute("DELETE FROM grades WHERE subject_id = ?", (id,))
        cursor.execute("DELETE FROM subjects WHERE id = ?", (id,))
        conn.commit()
    conn.close()
    return redirect(url_for('notenuebersicht'))

#Note hinzufügen
@app.route("/grades/add/<int:subject_id>", methods=["POST"])
def add_grade(subject_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    grade = request.form.get("grade")
    grade_type = request.form.get("grade_type")
    
    if grade and grade_type:
        weight = 2 if grade_type == "Schulaufgabe" else 1
        conn = get_connection()
        cursor = conn.cursor()
        
        # Sicherheitsabfrage: Gehört das Fach dem aktuellen Nutzer?
        cursor.execute("SELECT id FROM subjects WHERE id = ? AND user_id = ?", (subject_id, session["user_id"]))
        if cursor.fetchone():
            cursor.execute(
                "INSERT INTO grades (subject_id, grade, weight, grade_type) VALUES (?, ?, ?, ?)",
                (subject_id, float(grade), weight, grade_type)
            )
            conn.commit()
        conn.close()
    return redirect(url_for('notenuebersicht'))

#Note löschen
@app.route("/grades/delete/<int:id>", methods=["POST"])
def delete_grade(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_connection()
    cursor = conn.cursor()
    # Sicherheitsabfrage: Gehört die Note einem Fach des aktuellen Nutzers?
    cursor.execute('''
        SELECT grades.id FROM grades 
        JOIN subjects ON grades.subject_id = subjects.id 
        WHERE grades.id = ? AND subjects.user_id = ?
    ''', (id, session["user_id"]))
    
    if cursor.fetchone():
        cursor.execute("DELETE FROM grades WHERE id = ?", (id,))
        conn.commit()
    conn.close()
    return redirect(url_for('notenuebersicht'))

#Starten des Programms/Applikation
if __name__ == "__main__":
    app.run(debug=True)

