#Hauptprogramm
import management

from flask import Flask, render_template
from db import create_tables, get_connection

app = Flask(__name__)

create_tables()

@app.route("/")
def menu():
    return render_template("menue.html")



if __name__ == "__main__":
    app.run(debug=True)

