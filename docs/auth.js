/* auth.js — sesión simple (sin verificación real).
   Se incluye en cada página con:  <script src="auth.js"></script>
   - Si no hay usuario guardado, redirige a login.html
   - Si hay usuario, muestra su nombre en la esquina superior derecha + botón "Salir" */
(function () {
  var KEY = "mentores_usuario";

  // Carpeta donde está este script (para encontrar login.html aunque la página esté en una subcarpeta)
  var script = document.currentScript;
  var base = script ? script.src.replace(/[^\/]*$/, "") : "";
  var loginUrl = base + "login.html";

  function getUser() {
    try { return JSON.parse(localStorage.getItem(KEY)); } catch (e) { return null; }
  }

  window.Auth = {
    getUser: getUser,
    login: function (nombre, correo) {
      localStorage.setItem(KEY, JSON.stringify({ nombre: nombre, correo: correo }));
    },
    logout: function () {
      localStorage.removeItem(KEY);
      location.href = loginUrl;
    }
  };

  var user = getUser();
  if (!user) {
    location.replace(loginUrl);
    return;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = base + "auth.css";
    document.head.appendChild(link);

    var box = document.createElement("div");
    box.className = "auth-badge";

    var name = document.createElement("span");
    name.className = "auth-badge__name";
    name.textContent = "👤 " + user.nombre;

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "auth-badge__logout";
    btn.textContent = "Salir";
    btn.addEventListener("click", window.Auth.logout);

    box.appendChild(name);
    box.appendChild(btn);
    document.body.appendChild(box);
  });
})();
