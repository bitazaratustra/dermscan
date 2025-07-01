// ------------------ Configuración de Endpoints ------------------
const API = {
  user: '/user',
  predict: '/upload',
  history: '/predictions',
  chat: '/chat/',
  appointment: '/appointments'
};

// ------------------ Manejo de Autenticación ------------------
const auth = {
  get token() {
    return localStorage.getItem('authToken');
  },
  get headers() {
    return {
      'Authorization': `Bearer ${this.token}`
    };
  },
  get role() {
    if (!this.token) return null;
    try {
      const payload = JSON.parse(atob(this.token.split('.')[1]));
      return payload.role || 'user';
    } catch (e) {
      return 'user';
    }
  },
  check() {
    if (!this.token) {
      window.location.href = '/static/login.html';
    }
  },
  logout() {
    localStorage.removeItem('authToken');
    window.location.href = '/static/login.html';
  }
};

// ------------------ Variables Globales ------------------
let currentPredictionId = null;
let chartInstance = null;

// ------------------ Funciones Principales ------------------

async function fetchUser() {
  try {
    const res = await fetch(API.user, { headers: auth.headers });
    if (!res.ok) return auth.logout();
    const user = await res.json();
    document.getElementById('user-name').textContent = user.full_name;
    document.getElementById('last-access').textContent = new Date().toLocaleString();
  } catch (err) {
    console.error('Error fetching user:', err);
    auth.logout();
  }
}

async function handleUpload(file) {
  const formData = new FormData();
  formData.append('file', file);

  showLoading();
  try {
    const res = await fetch(API.predict, {
      method: 'POST',
      headers: auth.headers,
      body: formData
    });

    if (!res.ok) {
      alert('Error procesando imagen');
      return;
    }

    const result = await res.json();
    updateDiagnosis(result);
    await fetchHistory();
  } finally {
    hideLoading();
  }
}

function updateDiagnosis(data) {
  currentPredictionId = data.id;
  document.getElementById('diagnosis-text').textContent = data.diagnosis;
  document.getElementById('confidence').textContent = `${(data.confidence * 100).toFixed(2)}%`;

  document.getElementById('btn-chat').onclick = () => askBot(data.id);
  document.getElementById('btn-appointment').onclick = () => showAppointmentModal(data.id);
}

async function fetchHistory() {
  try {
    const res = await fetch(API.history, { headers: auth.headers });
    if (!res.ok) return;

    const history = await res.json();
    const container = document.getElementById('medical-history');
    container.innerHTML = '';

    if (history.length === 0) {
      const p = document.createElement('p');
      p.id = 'no-history';
      p.className = 'text-gray-500 col-span-full';
      p.textContent = 'No se han registrado diagnósticos previos.';
      container.appendChild(p);
    } else {
      history.forEach(item => {
        const div = document.createElement('div');
        div.className = 'bg-gray-100 dark:bg-gray-700 p-4 rounded-lg mb-2';
        div.innerHTML = `
          <p><strong>Diagnóstico:</strong> ${item.diagnosis}</p>
          <p><strong>Confianza:</strong> ${(item.confidence * 100).toFixed(2)}%</p>
          <p class="text-sm text-gray-500 dark:text-gray-400">${new Date(item.created_at).toLocaleString()}</p>
        `;
        container.appendChild(div);
      });
      drawChart(history);
    }
  } catch (err) {
    console.error('Error al cargar historial:', err);
  }
}

// ------------------ Funciones para el Modal de Citas (Listado) ------------------

function openAppointmentsModal() {
  document.getElementById('appointments-modal').classList.remove('hidden');
}

function closeAppointmentsModal() {
  document.getElementById('appointments-modal').classList.add('hidden');
}

async function loadAppointments() {
  try {
    const res = await fetch('/appointments', { headers: auth.headers });
    if (!res.ok) {
      alert('Error al cargar citas');
      return;
    }

    const appointments = await res.json();
    const container = document.getElementById('appointments-list');
    const emptyMessage = document.getElementById('appointments-empty-message');

    container.innerHTML = '';

    if (appointments.length === 0) {
      emptyMessage.classList.remove('hidden');
    } else {
      emptyMessage.classList.add('hidden');
      appointments.forEach(a => {
        const row = document.createElement('tr');

        // Determinar clase de estado según el estado de la cita
        let statusClass = '';
        switch(a.status.toLowerCase()) {
          case 'pendiente':
            statusClass = 'text-yellow-600 bg-yellow-100';
            break;
          case 'confirmada':
            statusClass = 'text-green-600 bg-green-100';
            break;
          case 'cancelada':
            statusClass = 'text-red-600 bg-red-100';
            break;
          default:
            statusClass = 'text-gray-600 bg-gray-100';
        }

        row.innerHTML = `
          <td class="px-6 py-4 whitespace-nowrap">
            <div class="flex items-center">
              <div class="ml-4">
                <div class="text-sm font-medium text-gray-900">${a.user_full_name}</div>
              </div>
            </div>
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            <div class="text-sm text-gray-900">${a.diagnosis}</div>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            ${new Date(a.scheduled_time).toLocaleString()}
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">
              ${a.status}
            </span>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            ${(a.confidence*100).toFixed(2)}%
          </td>
        `;
        container.appendChild(row);
      });
    }
  } catch (err) {
    console.error('Error al cargar citas:', err);
    alert('Error al cargar citas');
  }
}

// Actualizar el evento del botón de citas
document.getElementById('loadAppointmentsBtn').addEventListener('click', async (e) => {
  e.preventDefault();
  await loadAppointments();
  openAppointmentsModal();
});

// ------------------ Funciones del Modal de Agendar Cita ------------------

/**
 * Muestra el modal de agendar cita y establece la fecha mínima (hoy, con hora y minuto).
 * @param {number} predictionId – ID de la predicción activa.
 */
function showAppointmentModal(predictionId) {
  currentPredictionId = predictionId;

  // Limpiamos posibles mensajes de error previos
  document.getElementById('appointment-error').classList.add('hidden');

  // Establecemos el valor mínimo del input como “ahora”
  const inputDate = document.getElementById('appointment-date');
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hour = String(now.getHours()).padStart(2, '0');
  const minute = String(now.getMinutes()).padStart(2, '0');
  inputDate.min = `${year}-${month}-${day}T${hour}:${minute}`;

  // Limpiamos valor previo y abrimos el modal
  inputDate.value = '';
  const modal = document.getElementById('appointment-modal');
  modal.classList.remove('hidden');
  modal.classList.remove('opacity-0');
}

/**
 * Cierra el modal de agendar cita con fade-out.
 */
function closeAppointmentModal() {
  const modal = document.getElementById('appointment-modal');
  modal.classList.add('opacity-0');
  setTimeout(() => {
    modal.classList.add('hidden');
  }, 200);
}

/**
 * Envía la petición para agendar cita al backend. Valida que la fecha/hora esté completa.
 */
async function scheduleAppointment() {
  const inputDate = document.getElementById('appointment-date');
  const errorMsg = document.getElementById('appointment-error');
  const selected = inputDate.value;

  if (!selected) {
    errorMsg.textContent = 'Por favor, seleccioná una fecha y hora.';
    errorMsg.classList.remove('hidden');
    return;
  }
  errorMsg.classList.add('hidden');

  const payload = {
    prediction_id: currentPredictionId,
    scheduled_time: selected
  };

  try {
    const res = await fetch(API.appointment, {
      method: 'POST',
      headers: {
        ...auth.headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (res.status === 201) {
      closeAppointmentModal();
      alert('✅ Cita agendada con éxito');
    } else if (res.status === 404) {
      const body = await res.json();
      errorMsg.textContent = body.detail || 'Predicción no encontrada';
      errorMsg.classList.remove('hidden');
    } else {
      const text = await res.text();
      console.error('Error al agendar cita:', text);
      alert('❌ Ocurrió un error al agendar la cita');
    }
  } catch (err) {
    console.error('Error de red al agendar cita:', err);
    alert('❌ Error de red. Intentá nuevamente más tarde.');
  }
}

// Listener para el botón “Agendar” dentro del modal
document
  .getElementById('confirm-appointment')
  .addEventListener('click', scheduleAppointment);

// Listener para cerrar modal con la tecla “Esc”
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    const modal = document.getElementById('appointment-modal');
    if (!modal.classList.contains('hidden')) {
      closeAppointmentModal();
    }
  }
});

// ------------------ Funciones del Modal de Bot ------------------

/**
 * Cierra el modal de recomendación simple del bot.
 */
function closeBotModal() {
  document.getElementById('bot-modal').classList.add('hidden');
}

/**
 * Muestra el overlay de “Procesando...”.
 */
function showLoading() {
  document.getElementById('loading-overlay').style.display = 'flex';
}

/**
 * Oculta el overlay de “Procesando...”.
 */
function hideLoading() {
  document.getElementById('loading-overlay').style.display = 'none';
}

/**
 * Cierra el modal de chat por completa.
 */
function closeChatModal() {
  document.getElementById('chat-modal').classList.add('hidden');
}

/**
 * Agrega un mensaje dentro del contenedor de chat, con distinto estilo
 * si proviene del bot (fromBot = true) o del usuario (fromBot = false).
 * @param {string} text – Texto del mensaje.
 * @param {boolean} [fromBot=true] – True si el mensaje viene del bot; false si es usuario.
 */
function addChatMessage(text, fromBot = true) {
  const container = document.getElementById('chat-messages');
  const msgDiv = document.createElement('div');
  msgDiv.className = `mb-3 flex ${fromBot ? 'justify-start' : 'justify-end'}`;

  const bubble = document.createElement('div');
  bubble.className = fromBot
    ? 'bg-blue-100 text-blue-900 rounded-r-xl rounded-bl-xl px-4 py-2 max-w-[80%]'
    : 'bg-gray-200 text-gray-800 rounded-l-xl rounded-br-xl px-4 py-2 max-w-[80%]';

  bubble.textContent = text;
  msgDiv.appendChild(bubble);
  container.appendChild(msgDiv);

  // Scroll automático al último mensaje
  container.scrollTop = container.scrollHeight;
}

// ------------------ Listener para “Enviar” dentro del Chat Modal ------------------

document.getElementById('send-chat-btn').addEventListener('click', async () => {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return alert('Escribí un mensaje antes de enviar');
  if (!currentPredictionId) return alert('No hay diagnóstico seleccionado para consultar al bot.');

  addChatMessage(text, false);
  input.value = '';

  showLoading();
  try {
    const payload = {
      prediction_id: currentPredictionId,
      user_message: text
    };

    const res = await fetch(API.chat, {
      method: 'POST',
      headers: {
        ...auth.headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error("Error response from /chat:", errorText);
      addChatMessage('Error al obtener respuesta del bot.', true);
      return;
    }

    const data = await res.json();
    addChatMessage(data.recommendation || 'No hay respuesta del bot.', true);

  } catch (error) {
    console.error("Error en askBot:", error);
    addChatMessage('Error de red al comunicarse con el bot.', true);
  } finally {
    hideLoading();
  }
});

// ------------------ Inicio del Chat ------------------

/**
 * Inicia el proceso de chat: guarda el predictionId y muestra el modal de chat.
 * @param {number} predictionId – ID de la predicción activa.
 */
async function askBot(predictionId) {
  currentPredictionId = predictionId;
  document.getElementById('chat-messages').innerHTML = '';
  document.getElementById('chat-input').value = '';
  document.getElementById('chat-modal').classList.remove('hidden');
  document.getElementById('chat-input').focus();
}

// ------------------ Función para dibujar el gráfico del historial ------------------

function drawChart(data) {
  const ctx = document.getElementById('chart').getContext('2d');
  if (chartInstance) chartInstance.destroy();

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(d => new Date(d.created_at).toLocaleDateString()),
      datasets: [{
        label: 'Confianza Diagnóstico',
        data: data.map(d => d.confidence * 100),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          title: { display: true, text: '%' }
        }
      }
    }
  });
}

// ------------------ Inicialización al cargar la página ------------------
document.addEventListener('DOMContentLoaded', async () => {
  // Si es médico, redirigir
  if (auth.role === 'doctor') {
    window.location.href = '/static/doctor_dashboard.html';
    return;
  }

  auth.check();
  await fetchUser();
  await fetchHistory();

  const fileInput = document.getElementById('file-input');
  fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (!file || !file.type.startsWith('image/')) {
      alert('Por favor sube un archivo de imagen válido');
      return;
    }

    const reader = new FileReader();
    reader.onload = e => {
      const preview = document.getElementById('preview');
      preview.src = e.target.result;
      preview.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
    handleUpload(file);
  });
});
