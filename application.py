"""Project2"""
import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from requests import request
from flask import *
from flask_socketio import *

from collections import deque
from funciones import login_required

app = Flask(__name__)
app.config["SECRET_KEY"] = "SecretKey"
socketio = SocketIO(app)

channelsCreated = []
usersLogged = []
channelsMessages = dict()

limit = [100]

channelsCreated.append('Public')
channelsMessages['Public'] = [100]

# ruta redirecciona al index
# verifica al usuario con la funcion
@app.route("/")
@login_required
def index():
    return render_template("index.html", channels=channelsCreated)

# ruta para registrarse
@app.route("/registrarse", methods=['GET', 'POST'])
def registrarse():
    # Eliminamos la sesion pasada
    session.clear()

    username = request.form.get("username")

    if request.method == "POST":

        # verificamos que el username este bien
        if len(username) < 1 or username == '':
            return render_template("error.html", message="Username empty")

        if username in usersLogged:
            return render_template("error.html", message="Username already exists")

        usersLogged.append(username)

        session['username'] = username

        # Recuerda la sesión del usuario en una cookie si el navegador está cerrado.
        session.permanent = True

        return redirect("/channels/Public")
    else:
        return render_template("registrarse.html")

# ruta para el detalle personal de cambiar el nombre
# requerimos estar logueados
@app.route("/change", methods=['GET', 'POST'])
@login_required
def change():
    # recibimos username
    username = request.form.get("username")
    try:
        usersLogged.remove(session['username'])
    except ValueError:
        pass

    if request.method == "POST":
        # verificamos los caloress invalidos y mandamos errores
        if len(username) < 1 or username == '':
            return render_template("error.html")
        if username in usersLogged:
            return render_template("error.html")

        usersLogged.append(username)

        session['username'] = username

        return redirect("/")
    else:
        return render_template("change.html", channels=channelsCreated)

# logout
@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    try:
        usersLogged.remove(session['username'])
    except ValueError:
        pass

    return redirect("registrarse")

# ruta create para crear canales
@app.route("/create", methods=['GET', 'POST'])
@login_required
def create():
    # recibirmos el nuevo canal
    newChannel = request.form.get("channel")

    if request.method == "POST":
        # vemos si el canal ya existe
        if newChannel in channelsCreated:
            return render_template("error.html")
        if len(newChannel) == 0:
            return render_template("error.html")

        # agregamos el canal a la lista
        channelsCreated.append(newChannel)

        #  agregamos al diccionario
        channelsMessages[newChannel] = deque()
        return redirect("/channels/" + newChannel)
    else:
        return render_template("create.html", channels=channelsCreated)

# ruta de la pagina de canal
# requiere session
@app.route("/channels/<channel>", methods=['GET', 'POST'])
@login_required
def enter_channel(channel):
    user = session['username']

    # Actualiza el canal actual del usuario
    session['current_channel'] = channel

    if channel not in channelsCreated:
        return redirect("/channels/Public")

    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("channel.html", channels=channelsCreated, messages=channelsMessages[channel], usersLogged=usersLogged, user=user)

# Ruta
@socketio.on("joined", namespace='/')
def joined():
    # Guarde el canal actual para unirse a la sala.
    room = session.get('current_channel')

    join_room(room)

    emit('status', {
        'userJoined': session.get('username'),
        'channel': room,
        'msg': session.get('username') + ' ha entrado al canal'},
        room=room)

# Enviar mensajes
@socketio.on('send message')
def send_msg(msg, timestamp):
    # Enviar solo a usuarios en el mismo canal
    room = session.get('current_channel')

    # guardamos mensaje
    channelsMessages[room].append([timestamp, session.get('username'), msg])

    emit('announce message', {
        'user': session.get('username'),
        'timestamp': timestamp,
        'msg': msg},
        room=room)

# salir del canal ( Se puede seguir accediendo )
@socketio.on("left", namespace='/')
def left():
    room = session.get('current_channel')

    leave_room(room)

    emit('status', {
        'msg': session.get('username') + ' ha salido del canal'},
        room=room)

# Iniciamos
if __name__ == "__main__":
    socketio.run(app)
