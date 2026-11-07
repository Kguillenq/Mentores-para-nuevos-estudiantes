/* ==========================================================
   Interfaz del recomendador de mentores
   ----------------------------------------------------------
   Flujo: el estudiante elige sus categorías (carrera, interés,
   necesidad académica, franja y semestre) y la página muestra
   los mentores con mayor compatibilidad y los motivos.

   El puntaje sale del MISMO modelo del backend (regresión
   logística entrenada en mentores/): js/modelo.js lo exporta
   y aquí se calcula la probabilidad con sus coeficientes.
   Sin servidor, sin inicio de sesión.
   ========================================================== */

(function () {
  'use strict';

  var M = window.MODELO;
  var P = M.modelo;

  // Color por categoría (solo presentación).
  var CAT_INTERES = {
    'Datos e IA': 'tech', 'Desarrollo web': 'tech', 'Emprendimiento': 'mkt',
    'Salud y bienestar': 'robot', 'Investigación': 'vr'
  };
  var CAT_NECESIDAD = {
    'Cálculo': 'tech', 'Programación': 'robot', 'Estadística': 'vr',
    'Técnicas de estudio': 'mkt', 'Redacción académica': 'tech'
  };
  var DESC_NECESIDAD = {
    'Cálculo': 'Límites, derivadas e integrales de los primeros semestres.',
    'Programación': 'Lógica, algoritmos y tus primeros proyectos de código.',
    'Estadística': 'Probabilidad, análisis de datos e interpretación.',
    'Técnicas de estudio': 'Organizar tu tiempo y estudiar de forma efectiva.',
    'Redacción académica': 'Informes, ensayos y uso de fuentes.'
  };
  var SIGLAS = {
    'Ingeniería Informática': 'II', 'Ingeniería Comercial': 'IC', 'Psicología': 'PS',
    'Enfermería': 'EN', 'Derecho': 'DE'
  };
  var SEMESTRES = [1, 2];       // alcance del prototipo: estudiantes de 1.º y 2.º semestre
  var OPCIONES_K = [3, 5, 10];

  var state = { screen: 'form', carrera: null, interes: null, necesidad: null, franja: null,
                semestre: 1, k: 3, errores: [] };

  // ---------- Utilidades ----------

  function el(id) { return document.getElementById(id); }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function ord(n) { return n + '.º'; }

  // ---------- Modelo (réplica exacta de recomendador.py) ----------

  function probabilidad(est, men) {
    var c = P.coef;
    var dif = men.semestre - est.semestre;
    var z = P.intercepto +
      c.dif_semestres * (dif - P.media_dif_semestres) / P.desv_dif_semestres +
      c.misma_carrera * (est.carrera === men.carrera ? 1 : 0) +
      c.mismo_interes * (est.interes === men.interes ? 1 : 0) +
      c.cubre_necesidad * (est.necesidad === men.especialidad ? 1 : 0) +
      c.misma_franja * (est.franja === men.franja ? 1 : 0);
    return 1 / (1 + Math.exp(-z));
  }

  // Misma validación que validar_entrada(): si falta algo, no se calcula nada.
  function validar() {
    var e = [];
    if (!state.carrera) e.push('carrera');
    if (!state.interes) e.push('área de interés');
    if (!state.necesidad) e.push('necesidad académica');
    if (!state.franja) e.push('franja horaria');
    return e;
  }

  function recomendar() {
    var semMax = Math.max.apply(null, M.catalogo.map(function (m) { return m.semestre; })) - 1;
    var advertencias = [];
    if (state.semestre < M.sem_min_est || state.semestre > semMax) return null;
    if (state.semestre < M.sem_entrenamiento[0] || state.semestre > M.sem_entrenamiento[1]) {
      advertencias.push('Tu semestre está fuera del rango visto en el entrenamiento; la recomendación es una extrapolación.');
    }

    var cand = M.catalogo.filter(function (m) { return m.semestre > state.semestre; });
    var puntuados = cand.map(function (m, i) {
      return { m: m, i: i, p: probabilidad(state, m) };
    });
    // Orden descendente por probabilidad; los empates conservan el orden del catálogo (como argsort estable).
    puntuados.sort(function (a, b) { return (b.p - a.p) || (a.i - b.i); });
    var top = puntuados.slice(0, state.k).map(function (r) {
      var m = r.m, motivos = [];
      if (m.carrera === state.carrera) motivos.push('misma carrera');
      if (m.interes === state.interes) motivos.push('comparte interés en ' + state.interes);
      if (m.especialidad === state.necesidad) motivos.push('puede reforzar ' + state.necesidad);
      if (m.franja === state.franja) motivos.push('disponible en la franja ' + state.franja);
      return { m: m, p: r.p, motivos: motivos };
    });
    if (top.length && Math.round(top[0].p * 1000) / 1000 < M.umbral_aviso) {
      advertencias.push('Ningún mentor disponible supera ' + Math.round(M.umbral_aviso * 100) +
        '% de compatibilidad; considera ampliar la franja horaria o hablar con la coordinación.');
    }
    return { n: cand.length, top: top, advertencias: advertencias };
  }

  function resumen() {
    var bits = [];
    if (state.carrera) bits.push(state.carrera);
    if (state.interes) bits.push(state.interes);
    if (state.necesidad) bits.push(state.necesidad);
    if (state.franja) bits.push('franja ' + state.franja.toLowerCase());
    bits.push(ord(state.semestre) + ' semestre');
    return bits;
  }

  // ---------- Vistas ----------

  function renderSteps() {
    el('steps').innerHTML =
      '<span class="step-pill' + (state.screen === 'form' ? ' is-active' : '') + '">1 · Tu perfil</span>' +
      '<span class="step-pill' + (state.screen === 'results' ? ' is-active' : '') + '">2 · Tus mentores</span>';
  }

  function heroStep(num, cls, text) {
    return '<div class="hero-step"><span class="hero-step__num ' + cls + '">' + num + '</span><span>' + text + '</span></div>';
  }

  function renderHero() {
    if (state.screen === 'form') {
      el('hero').innerHTML =
        '<div class="hero__inner">' +
          '<div class="hero__text">' +
            '<span class="hero__badge">Mentores de semestres superiores</span>' +
            '<h1 class="hero__title">Encuentra al mentor que mejor te acompaña</h1>' +
            '<p class="hero__lead">Elige tu carrera, tus intereses y lo que necesitas reforzar. Te mostramos los mentores con mayor compatibilidad contigo y te explicamos por qué.</p>' +
          '</div>' +
          '<div class="hero__steps">' +
            heroStep('1', 'num-gold', 'Selecciona tus categorías') +
            heroStep('2', 'num-teal', 'Mira tus mentores con mayor afinidad') +
            heroStep('3', 'num-lilac', 'Revisa los motivos de cada recomendación') +
          '</div>' +
        '</div>';
    } else {
      el('hero').innerHTML =
        '<div class="hero__inner">' +
          '<div class="hero__text">' +
            '<h1 class="hero__title hero__title--small">Tus mentores recomendados</h1>' +
            '<p class="hero__lead">Según tu perfil: ' + esc(resumen().join(' · ')) + '.</p>' +
          '</div>' +
          '<button type="button" class="btn-gold" data-action="go-form">Editar mi perfil</button>' +
        '</div>';
    }
  }

  function chips(lista, actual, action, catMap) {
    return lista.map(function (v) {
      var on = actual === v;
      var cls = catMap ? 'chip cat-' + catMap[v] : 'chip chip--plain';
      return '<button type="button" class="' + cls + (on ? ' is-on' : '') + '" data-action="' + action +
        '" data-value="' + esc(v) + '" aria-pressed="' + on + '">' + esc(v) + '</button>';
    }).join('');
  }

  function renderAside() {
    var c = P.coef;
    var filas = [
      ['Cubre lo que necesitas reforzar', c.cubre_necesidad, '#0F7A6D'],
      ['Misma carrera', c.misma_carrera, '#1E5AA8'],
      ['Mismo interés', c.mismo_interes, '#6B4E9B'],
      ['Misma franja horaria', c.misma_franja, '#B07A00']
    ];
    var max = c.cubre_necesidad;
    var barras = filas.map(function (f) {
      return '<div><div class="weight__row"><span>' + f[0] + '</span><strong>' + f[1].toFixed(2) + '</strong></div>' +
        '<div class="weight__track"><div class="weight__fill" style="background:' + f[2] + ';width:' +
        Math.round(100 * f[1] / max) + '%"></div></div></div>';
    }).join('');
    return '<aside class="aside">' +
      '<h2 class="aside__title">Cómo se calcula la compatibilidad</h2>' +
      '<p class="aside__text">Un modelo de regresión logística compara tu perfil con cada mentor y estima una probabilidad de compatibilidad. Esto es lo que más pesa en el modelo entrenado:</p>' +
      '<div class="weights">' + barras + '</div>' +
      '<p class="aside__text">Además, cada semestre de diferencia con el mentor resta un poco (' + (c.dif_semestres / P.desv_dif_semestres).toFixed(3) + ' por semestre en el modelo).</p>' +
      '<div class="aside__rule"></div>' +
      '<p class="aside__note">Los datos de entrenamiento son <strong>sintéticos</strong>: la compatibilidad ordena opciones, no garantiza el éxito de una mentoría.</p>' +
    '</aside>';
  }

  function renderForm() {
    var necesidades = M.necesidades.map(function (v) {
      var on = state.necesidad === v;
      return '<button type="button" class="option cat-' + CAT_NECESIDAD[v] + (on ? ' is-on' : '') +
        '" data-action="set-necesidad" data-value="' + esc(v) + '" aria-pressed="' + on + '">' +
        '<span class="option__label">' + esc(v) + '</span>' +
        '<span class="option__desc">' + esc(DESC_NECESIDAD[v] || '') + '</span></button>';
    }).join('');

    var semestres = SEMESTRES.map(function (s) {
      var on = state.semestre === s;
      return '<button type="button" class="chip chip--plain' + (on ? ' is-on' : '') + '" data-action="set-semestre" data-value="' +
        s + '" aria-pressed="' + on + '">' + ord(s) + ' semestre</button>';
    }).join('');

    var ks = OPCIONES_K.map(function (k) {
      var on = state.k === k;
      return '<button type="button" class="chip chip--plain' + (on ? ' is-on' : '') + '" data-action="set-k" data-value="' +
        k + '" aria-pressed="' + on + '">' + k + ' mentores</button>';
    }).join('');

    var error = state.errores.length
      ? '<div class="field-error" role="alert">Antes de continuar, elige: ' + esc(state.errores.join(', ')) + '.</div>'
      : '';

    el('app').innerHTML =
      '<div class="layout">' +
        '<section class="form-col">' +
          '<div class="card">' +
            '<div class="card__head"><span class="card__num num-gold">1</span><h2 class="card__title">Tu carrera</h2></div>' +
            '<div class="chips">' + chips(M.carreras, state.carrera, 'set-carrera') + '</div>' +
          '</div>' +
          '<div class="card">' +
            '<div class="card__head"><span class="card__num num-teal">2</span><h2 class="card__title">Tu área de interés</h2></div>' +
            '<p class="card__hint">Elige el área que más te interesa. Los colores te ayudan a reconocerla en los resultados.</p>' +
            '<div class="chips">' + chips(M.intereses, state.interes, 'set-interes', CAT_INTERES) + '</div>' +
          '</div>' +
          '<div class="card">' +
            '<div class="card__head"><span class="card__num num-lilac">3</span><h2 class="card__title">¿Qué necesitas reforzar?</h2></div>' +
            '<div class="options">' + necesidades + '</div>' +
          '</div>' +
          '<div class="card">' +
            '<div class="card__head"><span class="card__num num-gold">4</span><h2 class="card__title">Disponibilidad y preferencias</h2></div>' +
            '<div class="group">' +
              '<div class="group__col"><span class="group__label">Franja horaria</span><div class="chips">' + chips(M.franjas, state.franja, 'set-franja') + '</div></div>' +
              '<div class="group__col"><span class="group__label">Semestre que cursas</span><div class="chips">' + semestres + '</div></div>' +
              '<div class="group__col"><span class="group__label">Cuántos mentores quieres ver</span><div class="chips">' + ks + '</div></div>' +
            '</div>' +
          '</div>' +
          error +
          '<div class="cta-row">' +
            '<button type="button" class="btn-primary" data-action="go-results">Ver mis mentores</button>' +
            '<span class="cta-row__summary">' + esc(resumen().join(' · ')) + '</span>' +
          '</div>' +
        '</section>' +
        renderAside() +
      '</div>';
  }

  function renderResults() {
    var r = recomendar();
    if (!r) { state.screen = 'form'; render(); return; }

    var avisos = r.advertencias.map(function (a) { return '<div class="notice">⚠️ ' + esc(a) + '</div>'; }).join('');

    var cards = r.top.map(function (x, i) {
      var m = x.m;
      var pct = Math.round(x.p * 1000) / 10;
      var cat = CAT_INTERES[m.interes];
      var okNec = m.especialidad === state.necesidad;
      var okFr = m.franja === state.franja;
      var okCar = m.carrera === state.carrera;
      var motivos = x.motivos.length
        ? '<ul class="reasons">' + x.motivos.map(function (t) { return '<li>' + esc(t.charAt(0).toUpperCase() + t.slice(1)) + '</li>'; }).join('') + '</ul>'
        : '<p class="reason">Sin coincidencias directas con tu perfil.</p>';

      return '<article class="class-card cat-' + cat + '">' +
        '<div class="class-card__main">' +
          '<div class="class-card__head">' +
            '<span class="avatar" aria-hidden="true">' + esc(SIGLAS[m.carrera] || 'M') + '</span>' +
            '<div class="class-card__titles">' +
              '<h3 class="class-card__title">Mentor ' + esc(m.mentor_id) + '</h3>' +
              '<span class="class-card__mentor">' + esc(m.carrera) + ' · ' + ord(m.semestre) + ' semestre</span>' +
            '</div>' +
            '<span class="rank">#' + (i + 1) + '</span>' +
          '</div>' +
          '<div class="tags">' +
            '<span class="tag cat-' + cat + (m.interes === state.interes ? ' is-hit' : '') + '">Interés: ' + esc(m.interes) + '</span>' +
            '<span class="tag cat-' + (CAT_NECESIDAD[m.especialidad] || 'tech') + (okNec ? ' is-hit' : '') + '">Especialidad: ' + esc(m.especialidad) + '</span>' +
          '</div>' +
          '<div class="facts">' +
            '<span class="fact' + (okCar ? ' is-match cat-' + cat : '') + '"><strong>Carrera:</strong> ' + esc(m.carrera) + '</span>' +
            '<span class="fact"><strong>Semestre:</strong> ' + ord(m.semestre) + '</span>' +
            '<span class="fact' + (okFr ? ' is-match cat-' + cat : '') + '"><strong>Franja:</strong> ' + esc(m.franja) + '</span>' +
          '</div>' +
        '</div>' +
        '<div class="class-card__side">' +
          '<div class="score"><span class="score__label">Compatibilidad</span><span class="score__value">' + pct.toFixed(1) + '%</span></div>' +
          '<div class="bar" role="img" aria-label="Compatibilidad ' + pct.toFixed(1) + ' por ciento"><div class="bar__fill" style="width:' + pct + '%"></div></div>' +
          '<span class="reasons__title">Por qué te lo recomendamos</span>' +
          motivos +
        '</div>' +
      '</article>';
    }).join('');

    el('app').innerHTML =
      '<div class="results">' +
        avisos +
        '<p class="results__intro">' + r.top.length + ' mentores recomendados de ' + r.n + ' candidatos de semestres superiores al tuyo.</p>' +
        cards +
        '<p class="results__limit">' + esc(M.limitacion) + '</p>' +
      '</div>';
  }

  function render() {
    renderSteps();
    renderHero();
    if (state.screen === 'form') renderForm(); else renderResults();
  }

  function renderKeepingFocus(action, value) {
    render();
    var sel = '[data-action="' + action + '"]' + (value !== null ? '[data-value="' + String(value).replace(/"/g, '\\"') + '"]' : '');
    var t = document.querySelector(sel);
    if (t) t.focus();
  }

  // ---------- Eventos ----------

  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-action]');
    if (!t) return;
    var action = t.getAttribute('data-action');
    var value = t.getAttribute('data-value');

    if (action === 'set-carrera') state.carrera = value;
    else if (action === 'set-interes') state.interes = value;
    else if (action === 'set-necesidad') state.necesidad = value;
    else if (action === 'set-franja') state.franja = value;
    else if (action === 'set-semestre') state.semestre = parseInt(value, 10);
    else if (action === 'set-k') state.k = parseInt(value, 10);
    else if (action === 'go-results') {
      state.errores = validar();
      if (state.errores.length) { render(); return; }
      state.screen = 'results';
      render();
      window.scrollTo({ top: 0 });
      return;
    } else if (action === 'go-form') {
      state.screen = 'form';
      render();
      window.scrollTo({ top: 0 });
      return;
    }
    state.errores = [];
    renderKeepingFocus(action, value);
  });

  el('footer-note').textContent =
    'Prototipo académico (Proyecto Integrador DSI). Los mentores y los estudiantes del entrenamiento son datos sintéticos: ' +
    'no hay datos personales ni inicio de sesión. La compatibilidad es una probabilidad estimada por un modelo de regresión logística ' +
    'entrenado con una regla definida por el equipo, no mide el éxito real de una mentoría.';

  render();
})();
