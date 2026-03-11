#Hauptprogramm
import management

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def menu():
    return render_template("menue.html")


if __name__ == "__main__":
    app.run(debug=True)

