/* ==========================================================
   Lógica visual del prototipo (sin backend)
   - Estado en memoria: se pierde al recargar la página.
   - Dos pantallas: "form" (perfil) y "results" (clases recomendadas).
   ========================================================== */

(function () {
  'use strict';

  var D = window.MENTORIAS_DATA;
  var W = D.weights;

  var state = {
    screen: 'form',
    interests: [],
    need: null,
    avail: null,
    comm: null,
    enrolled: {}
  };

  // ---------- Utilidades ----------

  function find(list, id) {
    for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
    return null;
  }

  function el(id) { return document.getElementById(id); }

  // ---------- Puntaje de afinidad ----------
  // Regla ilustrativa: no es un modelo entrenado ni validado.

  function scoreMentors() {
    var list = D.mentors.map(function (m) {
      var overlap = m.expertise.filter(function (e) { return state.interests.indexOf(e) >= 0; });
      var expScore = state.interests.length
        ? W.expertise * (overlap.length / Math.min(state.interests.length, m.expertise.length))
        : 0;
      var needMatch = state.need && state.need === m.need;
      var availMatch = state.avail && state.avail === m.avail;
      var commMatch = state.comm && state.comm === m.comm;

      var pct = Math.round(
        expScore +
        (needMatch ? W.need : 0) +
        (availMatch ? W.frequency : 0) +
        (commMatch ? W.channel : 0)
      );

      var reasons = [];
      if (overlap.length) {
        reasons.push('especialidad en ' + overlap.map(function (e) { return find(D.interests, e).label; }).join(', '));
      }
      if (needMatch) reasons.push(find(D.needs, m.need).label.toLowerCase());
      if (availMatch) reasons.push(find(D.frequencies, m.avail).long.toLowerCase());
      if (commMatch) reasons.push('canal de apoyo por ' + find(D.channels, m.comm).label.toLowerCase());

      return { mentor: m, pct: pct, overlap: overlap, reasons: reasons };
    });

    list.sort(function (a, b) { return b.pct - a.pct; });
    return list;
  }

  function summaryBits() {
    var bits = [];
    if (state.interests.length) {
      bits.push(state.interests.length + (state.interests.length === 1 ? ' interés' : ' intereses'));
    }
    if (state.need) bits.push(find(D.needs, state.need).label.toLowerCase());
    if (state.avail) bits.push(find(D.frequencies, state.avail).long.toLowerCase());
    if (state.comm) bits.push('apoyo por ' + find(D.channels, state.comm).label.toLowerCase());
    return bits;
  }

  // ---------- Vistas ----------

  function renderSteps() {
    el('steps').innerHTML =
      '<span class="step-pill' + (state.screen === 'form' ? ' is-active' : '') + '">1 · Tu perfil</span>' +
      '<span class="step-pill' + (state.screen === 'results' ? ' is-active' : '') + '">2 · Clases recomendadas</span>';
  }

  function renderHero() {
    if (state.screen === 'form') {
      el('hero').innerHTML =
        '<div class="hero__inner">' +
          '<div class="hero__text">' +
            '<span class="hero__badge">Mentorías grupales para primer año</span>' +
            '<h1 class="hero__title">Aprende en grupo con mentores de cursos superiores</h1>' +
            '<p class="hero__lead">Cada mentor dirige una clase para un grupo de estudiantes. Te recomendamos las que mejor calzan con tus intereses, el tipo de sesión y la frecuencia que prefieres.</p>' +
          '</div>' +
          '<div class="hero__steps">' +
            heroStep('1', 'num-gold', 'Cuéntanos tu perfil') +
            heroStep('2', 'num-teal', 'Revisa las clases recomendadas') +
            heroStep('3', 'num-lilac', 'Inscríbete en tu grupo') +
          '</div>' +
        '</div>';
    } else {
      var bits = summaryBits();
      var line = bits.length
        ? 'Según tu perfil: ' + bits.join(' · ') + '.'
        : 'Completa tu perfil para afinar el orden.';
      el('hero').innerHTML =
        '<div class="hero__inner">' +
          '<div class="hero__text">' +
            '<h1 class="hero__title hero__title--small">Clases de mentoría para ti</h1>' +
            '<p class="hero__lead">' + line + '</p>' +
          '</div>' +
          '<button type="button" class="btn-gold" data-action="go-form">Editar mi perfil</button>' +
        '</div>';
    }
  }

  function heroStep(num, numClass, text) {
    return '<div class="hero-step"><span class="hero-step__num ' + numClass + '">' + num + '</span><span>' + text + '</span></div>';
  }

  function renderForm() {
    var interestChips = D.interests.map(function (d) {
      var on = state.interests.indexOf(d.id) >= 0;
      return '<button type="button" class="chip cat-' + d.cat + (on ? ' is-on' : '') +
        '" data-action="toggle-interest" data-id="' + d.id + '" aria-pressed="' + on + '">' + d.label + '</button>';
    }).join('');

    var needOptions = D.needs.map(function (d) {
      var on = state.need === d.id;
      return '<button type="button" class="option cat-' + d.cat + (on ? ' is-on' : '') +
        '" data-action="set-need" data-id="' + d.id + '" aria-pressed="' + on + '">' +
        '<span class="option__label">' + d.label + '</span>' +
        '<span class="option__desc">' + d.desc + '</span></button>';
    }).join('');

    var freqChips = D.frequencies.map(function (d) {
      var on = state.avail === d.id;
      return '<button type="button" class="chip chip--plain' + (on ? ' is-on' : '') +
        '" data-action="set-avail" data-id="' + d.id + '" aria-pressed="' + on + '">' + d.short + '</button>';
    }).join('');

    var chanChips = D.channels.map(function (d) {
      var on = state.comm === d.id;
      return '<button type="button" class="chip chip--plain' + (on ? ' is-on' : '') +
        '" data-action="set-comm" data-id="' + d.id + '" aria-pressed="' + on + '">' + d.label + '</button>';
    }).join('');

    var bits = summaryBits();
    var summary = bits.length ? 'Seleccionaste: ' + bits.join(' · ') : 'Aún no has elegido nada.';

    el('app').innerHTML =
      '<div class="layout">' +
        '<section class="form-col">' +

          '<div class="card">' +
            '<div class="card__head"><span class="card__num num-gold">1</span><h2 class="card__title">Tus intereses</h2></div>' +
            '<p class="card__hint">Elige todas las áreas que quieras trabajar en clase. Los colores indican el área del mentor.</p>' +
            '<div class="chips">' + interestChips + '</div>' +
          '</div>' +

          '<div class="card">' +
            '<div class="card__head"><span class="card__num num-teal">2</span><h2 class="card__title">¿Qué tipo de sesión buscas?</h2></div>' +
            '<div class="options">' + needOptions + '</div>' +
          '</div>' +

          '<div class="card">' +
            '<div class="card__head"><span class="card__num num-lilac">3</span><h2 class="card__title">Frecuencia y canal del grupo</h2></div>' +
            '<div class="group">' +
              '<div class="group__col"><span class="group__label">Frecuencia de las sesiones</span><div class="chips">' + freqChips + '</div></div>' +
              '<div class="group__col"><span class="group__label">Canal de apoyo del grupo</span><div class="chips">' + chanChips + '</div></div>' +
            '</div>' +
          '</div>' +

          '<div class="cta-row">' +
            '<button type="button" class="btn-primary" data-action="go-results">Ver clases recomendadas</button>' +
            '<span class="cta-row__summary">' + summary + '</span>' +
          '</div>' +

        '</section>' +
        renderAside() +
      '</div>';
  }

  function renderAside() {
    function row(label, value, color, widthPct) {
      return '<div><div class="weight__row"><span>' + label + '</span><strong>' + value + '</strong></div>' +
        '<div class="weight__track"><div class="weight__fill" style="background:' + color + ';width:' + widthPct + '%"></div></div></div>';
    }
    var max = W.expertise;
    return '<aside class="aside">' +
      '<h2 class="aside__title">Cómo se calcula la afinidad</h2>' +
      '<p class="aside__text">Cada clase recibe un puntaje de 0 a 100 según cuatro criterios de tu perfil, tomando como base al mentor que la dirige.</p>' +
      '<div class="weights">' +
        row('Áreas de especialidad', W.expertise, '#1E5AA8', 100 * W.expertise / max) +
        row('Tipo de sesión', W.need, '#0F7A6D', 100 * W.need / max) +
        row('Frecuencia de sesiones', W.frequency, '#6B4E9B', 100 * W.frequency / max) +
        row('Canal de apoyo', W.channel, '#B07A00', 100 * W.channel / max) +
      '</div>' +
      '<div class="aside__rule"></div>' +
      '<p class="aside__note">El género de los mentores no se usa para emparejar. Las ponderaciones son una regla ilustrativa del prototipo, no un modelo validado.</p>' +
    '</aside>';
  }

  function renderResults() {
    var cards = scoreMentors().map(function (s, i) {
      var m = s.mentor;
      var asked = !!state.enrolled[m.id];
      var taken = m.enrolled + (asked ? 1 : 0);
      var free = m.cap - taken;
      var seatsPct = Math.round(100 * taken / m.cap);

      var tags = m.expertise.map(function (e) {
        var d = find(D.interests, e);
        var hit = state.interests.indexOf(e) >= 0;
        return '<span class="tag cat-' + d.cat + (hit ? ' is-hit' : '') + '">' + d.label + '</span>';
      }).join('');

      var reason = s.reasons.length
        ? 'Coincide en: ' + s.reasons.join('; ') + '.'
        : 'Sin coincidencias directas con tu perfil.';

      return '<article class="class-card cat-' + m.area + '">' +
        '<div class="class-card__main">' +
          '<div class="class-card__head">' +
            '<span class="avatar" aria-hidden="true">' + m.initials + '</span>' +
            '<div class="class-card__titles">' +
              '<h3 class="class-card__title">' + m.title + '</h3>' +
              '<span class="class-card__mentor">Dirige ' + m.id + ' · ' + m.position + ' ' + m.level + ' · ' + m.years + ' años de experiencia</span>' +
            '</div>' +
            '<span class="rank">#' + (i + 1) + '</span>' +
          '</div>' +
          '<div class="tags">' + tags + '</div>' +
          '<div class="facts">' +
            fact('Tipo', find(D.needs, m.need).label) +
            fact('Horario', m.schedule) +
            fact('Frecuencia', find(D.frequencies, m.avail).long) +
            fact('Canal de apoyo', find(D.channels, m.comm).label) +
            fact('Lenguaje', m.language) +
          '</div>' +
        '</div>' +
        '<div class="class-card__side">' +
          '<div class="score"><span class="score__label">Afinidad</span><span class="score__value">' + s.pct + '%</span></div>' +
          '<div class="bar"><div class="bar__fill" style="width:' + s.pct + '%"></div></div>' +
          '<p class="reason">' + reason + '</p>' +
          '<div class="seats">' +
            '<span class="seats__text">' + free + ' de ' + m.cap + ' cupos disponibles</span>' +
            '<div class="bar bar--thin' + (free <= 3 ? ' is-low' : '') + '"><div class="bar__fill" style="width:' + seatsPct + '%"></div></div>' +
          '</div>' +
          '<button type="button" class="btn-enroll' + (asked ? ' is-done' : '') + '" data-action="enroll" data-id="' + m.id + '">' +
            (asked ? 'Inscripción confirmada' : 'Inscribirme en la clase') +
          '</button>' +
        '</div>' +
      '</article>';
    }).join('');

    el('app').innerHTML = '<div class="results">' + cards + '</div>';
  }

  function fact(label, value) {
    return '<span class="fact"><strong>' + label + ':</strong> ' + value + '</span>';
  }

  // ---------- Render general ----------

  function render() {
    renderSteps();
    renderHero();
    if (state.screen === 'form') renderForm(); else renderResults();
  }

  // Mantiene el foco en el botón pulsado al volver a dibujar.
  function renderKeepingFocus(action, id) {
    render();
    if (!action) return;
    var sel = '[data-action="' + action + '"]' + (id ? '[data-id="' + id + '"]' : '');
    var target = document.querySelector(sel);
    if (target) target.focus();
  }

  // ---------- Eventos ----------

  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-action]');
    if (!t) return;
    var action = t.getAttribute('data-action');
    var id = t.getAttribute('data-id');

    if (action === 'toggle-interest') {
      var i = state.interests.indexOf(id);
      if (i >= 0) state.interests.splice(i, 1); else state.interests.push(id);
    } else if (action === 'set-need') {
      state.need = id;
    } else if (action === 'set-avail') {
      state.avail = id;
    } else if (action === 'set-comm') {
      state.comm = id;
    } else if (action === 'enroll') {
      state.enrolled[id] = !state.enrolled[id];
    } else if (action === 'go-results') {
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

    renderKeepingFocus(action, id);
  });

  render();
})();
