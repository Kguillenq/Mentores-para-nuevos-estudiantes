/* ==========================================================
   Datos del prototipo
   ----------------------------------------------------------
   - Los 5 mentores salen de las primeras filas del dataset
     "Mentor Recommendation (IT Mentor-Mentee Matching)"
     (Hank Carter, Zenodo: https://zenodo.org/records/13942111).
   - Los campos `title`, `schedule`, `cap` y `enrolled` son DATOS DE
     EJEMPLO del prototipo: el dataset no los incluye.
   - Se omite el género de los mentores a propósito.
   ========================================================== */

window.MENTORIAS_DATA = {

  // Áreas de interés (vienen de la columna Expertise). `cat` define el color.
  interests: [
    { id: 'aws',  label: 'AWS',                 cat: 'tech'  },
    { id: 'ml',   label: 'Machine Learning',    cat: 'tech'  },
    { id: 'kin',  label: 'Robot Kinematics',    cat: 'robot' },
    { id: 'ctrl', label: 'Control Systems',     cat: 'robot' },
    { id: 'ar',   label: 'Augmented Reality',   cat: 'vr'    },
    { id: 'sim',  label: 'Simulation',          cat: 'vr'    },
    { id: 'dm',   label: 'Digital Marketing',   cat: 'mkt'   },
    { id: 'cms',  label: 'Content Management',  cat: 'mkt'   },
    { id: 'seo',  label: 'SEO Optimization',    cat: 'mkt'   }
  ],

  // Tipo de sesión (columna Mentoring_Preferences).
  needs: [
    { id: 'career',  label: 'Charla de orientación', desc: 'Decidir rumbo, ramos y primeras prácticas en grupo.', cat: 'mkt'   },
    { id: 'project', label: 'Taller de proyecto',    desc: 'Avanzar en un proyecto junto al grupo y el mentor.',  cat: 'robot' },
    { id: 'tech',    label: 'Clase técnica',         desc: 'Aprender herramientas y buenas prácticas en clase.',  cat: 'tech'  }
  ],

  // Frecuencia de sesiones (columna Availability).
  frequencies: [
    { id: 'full', short: 'Dos por semana',  long: 'Dos sesiones por semana' },
    { id: 'part', short: 'Una por semana',  long: 'Una sesión por semana'   },
    { id: 'free', short: 'Horario flexible', long: 'Horario flexible'       }
  ],

  // Canal de apoyo del grupo (columna Communication_Methods).
  channels: [
    { id: 'email', label: 'Correo' },
    { id: 'chat',  label: 'Chat'   }
  ],

  // Mentores / clases.
  mentors: [
    {
      id: 'Mentor_1', position: 'Cloud Engineer', initials: 'CE', area: 'tech',
      level: 'Senior', years: 12, expertise: ['aws'], language: 'Python',
      avail: 'full', need: 'career', comm: 'email',
      title: 'Rutas de carrera en la nube con AWS',
      schedule: 'Martes y jueves · 17:30', cap: 25, enrolled: 19
    },
    {
      id: 'Mentor_2', position: 'E-commerce Specialist', initials: 'ES', area: 'mkt',
      level: 'Nivel medio', years: 6, expertise: ['dm', 'cms', 'seo'], language: 'HTML',
      avail: 'part', need: 'career', comm: 'email',
      title: 'Carreras en marketing digital: SEO y contenidos',
      schedule: 'Miércoles · 18:00', cap: 20, enrolled: 9
    },
    {
      id: 'Mentor_3', position: 'AR/VR Developer', initials: 'AR', area: 'vr',
      level: 'Lead', years: 20, expertise: ['ar', 'sim'], language: 'C#',
      avail: 'free', need: 'project', comm: 'chat',
      title: 'Taller de proyecto: realidad aumentada y simulación',
      schedule: 'A coordinar con el grupo', cap: 15, enrolled: 12
    },
    {
      id: 'Mentor_4', position: 'Robotics Engineer', initials: 'RE', area: 'robot',
      level: 'Lead', years: 16, expertise: ['ml'], language: 'C',
      avail: 'part', need: 'tech', comm: 'email',
      title: 'Clase técnica: machine learning aplicado a robótica',
      schedule: 'Lunes · 18:00', cap: 30, enrolled: 18
    },
    {
      id: 'Mentor_5', position: 'Robotics Engineer', initials: 'RE', area: 'robot',
      level: 'Senior', years: 9, expertise: ['kin', 'ctrl', 'ml'], language: 'Python',
      avail: 'free', need: 'project', comm: 'email',
      title: 'Taller de proyecto: control y cinemática de robots',
      schedule: 'A coordinar con el grupo', cap: 12, enrolled: 10
    }
  ],

  // Ponderaciones ilustrativas del puntaje de afinidad (suman 100).
  weights: { expertise: 40, need: 30, frequency: 15, channel: 15 }
};
