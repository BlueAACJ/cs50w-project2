document.addEventListener("DOMContentLoaded", () => {
  // Conectarse a websocket
  var socket = io.connect(
    location.protocol + "//" + document.domain + ":" + location.port
  );

  // configuracion del boton
  socket.on("connect", () => {
    // usuario se une
    socket.emit("joined");

    // eliminar el último canal del usuario
    document.querySelector("#newChannel").addEventListener("click", () => {
      localStorage.removeItem("last_channel");
    });

    // Cuando la usuario deja el canal redirigir a '/'
    document.querySelector("#leave").addEventListener("click", () => {
      socket.emit("left");

      localStorage.removeItem("last_channel");
      window.location.replace("/");
    });

    // Enviar mensaje con el enter
    document.querySelector("#comment").addEventListener("keydown", (event) => {
      if (event.key == "Enter") {
        document.getElementById("send-button").click();
      }
    });

    // emitir evento enviar mensaje
    document.querySelector("#send-button").addEventListener("click", () => {
      let timestamp = new Date();
      timestamp = timestamp.toLocaleTimeString();

      // guardar mensaje
      let msg = document.getElementById("comment").value;
      socket.emit("send message", msg, timestamp);

      // limpiar entrada
      document.getElementById("comment").value = "";
    });
  });

  socket.on("status", (data) => {
    // usuario unido

    infoMessage(data.msg);

    // Guardar el canal actual del usuario en localStorage
    localStorage.setItem("last_channel", data.channel);
  });

  socket.on("announce message", (data) => {
    // formato del mensaje
    let timestamp = data.timestamp;
    let userMessage = data.user;
    let message = data.msg;

    createMessage(timestamp, userMessage, message);
  });

  function createMessage(timestamp, user, msg) {
    let ul = document.querySelector("#chat");
    let li = document.createElement("li");
    let p = document.createElement("p");

    user = user.charAt(0).toUpperCase() + user.slice(1);

    let pUser = createElement("strong", "user", user);
    let pMsg = createElement("span", "msg", msg);
    let pTimestamp = createElement("small", "time", timestamp);

    let br = document.createElement("br");

    li.appendChild(pUser);
    li.appendChild(document.createTextNode(" "));
    li.appendChild(pTimestamp);
    li.appendChild(br);
    li.appendChild(pMsg);

    li.setAttribute("class", "messageBox");

    ul.append(li);
  }

  function createElement(element, cls, text) {
    let el = document.createElement(element);
    el.appendChild(document.createTextNode(text));
    el.setAttribute("class", cls);

    return el;
  }

  function infoMessage(msg) {
    let chat = document.querySelector("#chat");
    let message = createElement("p", "message-info", msg);
    chat.appendChild(message);
  }
});
