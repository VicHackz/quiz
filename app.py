import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_socketio import SocketIO

app = Flask(__name__)
app.secret_key = "superhemligt"
socketio = SocketIO(app)

USERS = {
    "Lag1": "HATAGAIS",
    "Lag2": "HATAGAIS",
    "Lag3": "HATAGAIS",
    "Lag4": "HATAGAIS",
    "admin": "admin"
}

first_team = None

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USERS and USERS[username] == password:
            session['user'] = username
            if username == "admin":
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("game"))
        else:
            return render_template("login.html", error="Fel användarnamn eller lösenord.")
    return render_template("login.html")

@app.route("/game")
def game():
    if "user" not in session or session["user"] == "admin":
        return redirect(url_for("login"))
    team_display = session["user"].replace("Lag", "Lag ")
    return render_template("index.html", team=team_display)

@app.route("/admin")
def admin():
    if "user" not in session or session["user"] != "admin":
        return redirect(url_for("login"))
    return render_template(
        "admin.html",
        first_team=first_team
    )

@app.route('/bild.jpeg')
def serve_image():
    return send_from_directory('.', 'bild.jpeg')

# ------- SocketIO-händelser -------

@socketio.on("buzz")
def handle_buzz(team_name):
    global first_team
    if team_name == "admin":
        return
    if first_team is None:
        first_team = team_name
        socketio.emit("buzzed", team_name)

@socketio.on("reset")
def handle_reset():
    global first_team
    first_team = None
    socketio.emit("reset")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)