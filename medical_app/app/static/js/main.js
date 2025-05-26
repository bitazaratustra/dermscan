const API = {
  user: '/user',
  predict: '/upload',
  history: '/predictions',
  chat: '/chat',
  appointment: '/appointments'
};

const auth = {
  get token() {
    return localStorage.getItem('authToken');
  },
  get headers() {
    return {
      'Authorization': `Bearer ${this.token}`
    };
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

    if (!res.ok) return alert('Error procesando imagen');

    const result = await res.json();
    updateDiagnosis(result);
    await fetchHistory();
  } finally {
    hideLoading();
  }
}

function updateDiagnosis(data) {
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
  } catch (err) {
    console.error('Error al cargar historial:', err);
  }
}

async function askBot(predictionId) {
  showLoading();
  try {
    const res = await fetch(API.chat, {
      method: 'POST',
      headers: {
        ...auth.headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ prediction_id: predictionId })
    });

    if (!res.ok) return alert('Error al consultar al bot');

    const data = await res.json();
    showBotResponse(data.recommendation);
  } finally {
    hideLoading();
  }
}

// Agendamiento de citas
let currentPredictionId = null;

function showAppointmentModal(predictionId) {
  currentPredictionId = predictionId;
  document.getElementById('appointment-modal').classList.remove('hidden');
}

function closeAppointmentModal() {
  document.getElementById('appointment-modal').classList.add('hidden');
}

async function scheduleAppointment(predictionId, date) {
  try {
    const res = await fetch(API.appointment, {
      method: 'POST',
      headers: {
        ...auth.headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ prediction_id: predictionId, scheduled_time: date })
    });

    if (!res.ok) return alert('Error al agendar cita');
    alert('Cita agendada con éxito');
  } catch (err) {
    console.error('Error al agendar cita:', err);
    alert('Ocurrió un error');
  }
}

document.getElementById('confirm-appointment').addEventListener('click', () => {
  const date = document.getElementById('appointment-date').value;
  if (!date) return alert('Por favor seleccioná fecha y hora');
  scheduleAppointment(currentPredictionId, date);
  closeAppointmentModal();
});

// Bot response modal
function showBotResponse(message) {
  document.getElementById('bot-response').textContent = message;
  document.getElementById('bot-modal').classList.remove('hidden');
}

function closeBotModal() {
  document.getElementById('bot-modal').classList.add('hidden');
}

// Loading overlay
function showLoading() {
  document.getElementById('loading-overlay').style.display = 'flex';
}
function hideLoading() {
  document.getElementById('loading-overlay').style.display = 'none';
}

// Mostrar modal de chat
function showChatModal() {
  document.getElementById('chat-modal').classList.remove('hidden');
  document.getElementById('chat-input').value = '';
  document.getElementById('chat-messages').innerHTML = '';
  document.getElementById('chat-input').focus();
}

// Cerrar modal de chat
function closeChatModal() {
  document.getElementById('chat-modal').classList.add('hidden');
}

// Mostrar mensaje en el chat
function addChatMessage(text, fromBot = true) {
  const container = document.getElementById('chat-messages');
  const msgDiv = document.createElement('div');
  msgDiv.className = fromBot ? 'mb-2 p-2 bg-blue-100 rounded text-blue-900' : 'mb-2 p-2 bg-gray-300 rounded text-gray-800 text-right';
  msgDiv.textContent = text;
  container.appendChild(msgDiv);
  container.scrollTop = container.scrollHeight;
}

// Manejar envío de mensaje
document.getElementById('send-chat-btn').addEventListener('click', async () => {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;

  addChatMessage(text, false); // mensaje usuario
  input.value = '';

  // Simulación o llamada real al backend
  try {
    const res = await fetch(API.chat, {
      method: 'POST',
      headers: {
        ...auth.headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: text }) // ajustar segun backend
    });

    if (!res.ok) {
      addChatMessage('Error al obtener respuesta del bot.');
      return;
    }
    const data = await res.json();
    addChatMessage(data.reply || 'No hay respuesta del bot.');
  } catch (error) {
    addChatMessage('Error de red al comunicarse con el bot.');
  }
});

// Abrir modal al click en botón Consultar al bot
document.getElementById('btn-chat').addEventListener('click', () => {
  showChatModal();
});


// Chart
let chartInstance;
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

// Inicialización
document.addEventListener('DOMContentLoaded', async () => {
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
