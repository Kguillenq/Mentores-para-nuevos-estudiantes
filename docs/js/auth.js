/* auth.js — sesión simple (sin verificación real).
   Se incluye en index.html con:  <script src="js/auth.js"></script>
   - Si no hay usuario guardado, redirige a login.html
   - Si hay usuario, muestra su nombre en la barra superior (esquina derecha) + botón "Salir" */
(function () {
  'use strict';

  var KEY = 'mentores_usuario';

  // Carpeta de este script (docs/js/). login.html y css/ están un nivel más arriba.
  var script = document.currentScript;
  var base = script ? script.src.replace(/[^\/]*$/, '') : '';
  var loginUrl = base + '../login.html';
  var cssUrl = base + '../css/auth.css';

  function getUser() {
    try { return JSON.parse(localStorage.getItem(KEY)); } catch (e) { return null; }
  }

  window.Auth = {
    getUser: getUser,
    logout: function () {
      try { localStorage.removeItem(KEY); } catch (e) {}
      location.href = loginUrl;
    }
  };

  var user = getUser();
  if (!user) {
    location.replace(loginUrl);
    return;
  }

  document.addEventListener('DOMContentLoaded', function () {
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = cssUrl;
    document.head.appendChild(link);

    var box = document.createElement('div');
    box.className = 'auth-badge';

    var name = document.createElement('span');
    name.className = 'auth-badge__name';
    name.textContent = user.nombre;
    name.title = user.correo || '';

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'auth-badge__logout';
    btn.textContent = 'Salir';
    btn.addEventListener('click', window.Auth.logout);

    box.appendChild(name);
    box.appendChild(btn);

    // Dentro de la barra superior si existe; si no, flotando arriba a la derecha.
    var bar = document.querySelector('.topbar');
    if (bar) {
      box.classList.add('auth-badge--inline');
      bar.appendChild(box);
    } else {
      document.body.appendChild(box);
    }
  });
})();
