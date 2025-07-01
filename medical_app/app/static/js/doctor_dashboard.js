// ------------------ Configuración de Endpoints ------------------
const API = {
  doctorProfile: '/doctor/me',
  doctorAppointments: '/doctor/appointments',
  updateAppointment: '/doctor/appointments/'
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

// ------------------ Funciones Médicas ------------------

async function fetchDoctorProfile() {
  try {
    const res = await fetch(API.doctorProfile, { headers: auth.headers });
    if (!res.ok) throw new Error('Error cargando perfil');
    const doctor = await res.json();
    document.getElementById('doctor-name').textContent = doctor.full_name;
    document.getElementById('doctor-specialty').textContent = doctor.specialty || 'Dermatología';
    document.getElementById('navbar-doctor-name').textContent = doctor.full_name;
  } catch (err) {
    console.error('Error fetching doctor profile:', err);
  }
}

async function loadDoctorAppointments() {
  try {
    const res = await fetch(API.doctorAppointments, { headers: auth.headers });
    if (!res.ok) throw new Error('Error cargando citas');
    const appointments = await res.json();
    renderAppointments(appointments);
  } catch (err) {
    console.error('Error loading appointments:', err);
    alert('Error al cargar citas');
  }
}

function renderAppointments(appointments) {
  const container = document.getElementById('appointments-container');
  container.innerHTML = '';

  if (appointments.length === 0) {
    document.getElementById('no-appointments').classList.remove('hidden');
    return;
  }

  document.getElementById('no-appointments').classList.add('hidden');

  appointments.forEach(appointment => {
    const row = document.createElement('tr');
    row.className = 'hover:bg-gray-50';

    let statusClass = '';
    switch(appointment.status.toLowerCase()) {
      case 'pendiente': statusClass = 'bg-yellow-100 text-yellow-800'; break;
      case 'confirmada': statusClass = 'bg-green-100 text-green-800'; break;
      case 'cancelada': statusClass = 'bg-red-100 text-red-800'; break;
      case 'completada': statusClass = 'bg-blue-100 text-blue-800'; break;
    }

    // Construir URL de la imagen
    const imageUrl = appointment.image_filename ?
      `/static/uploads/${appointment.image_filename}` :
      null;

    // Formatear fecha y hora
    const dateTime = new Date(appointment.scheduled_time);
    const formattedDate = dateTime.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
    const formattedTime = dateTime.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });

    row.innerHTML = `
      <td class="px-4 py-2 border-b">${appointment.user_full_name}</td>
      <td class="px-4 py-2 border-b">${appointment.diagnosis}</td>
      <td class="px-4 py-2 border-b">${(appointment.confidence * 100).toFixed(2)}%</td>
      <td class="px-4 py-2 border-b">${formattedDate} ${formattedTime}</td>
      <td class="px-4 py-2 border-b">
        ${imageUrl ?
          `<button class="text-blue-500 hover:text-blue-700 view-image-btn" data-url="${imageUrl}">
            <i class="fas fa-eye mr-1"></i> Ver imagen
          </button>` :
          'Sin imagen'}
      </td>
      <td class="px-4 py-2 border-b">
        <span class="px-2 py-1 rounded ${statusClass}">${appointment.status}</span>
      </td>
      <td class="px-4 py-2 border-b">
        <select class="status-select border rounded p-1" data-id="${appointment.id}">
          <option value="pendiente" ${appointment.status === 'pendiente' ? 'selected' : ''}>Pendiente</option>
          <option value="confirmada" ${appointment.status === 'confirmada' ? 'selected' : ''}>Confirmada</option>
          <option value="cancelada" ${appointment.status === 'cancelada' ? 'selected' : ''}>Cancelada</option>
          <option value="completada" ${appointment.status === 'completada' ? 'selected' : ''}>Completada</option>
        </select>
      </td>
    `;
    container.appendChild(row);
  });

  // Event listeners para los botones de ver imagen
  document.querySelectorAll('.view-image-btn').forEach(button => {
    button.addEventListener('click', function() {
      const imageUrl = this.getAttribute('data-url');
      openImageModal(imageUrl);
    });
  });

  document.querySelectorAll('.status-select').forEach(select => {
    select.addEventListener('change', (e) => {
      updateAppointmentStatus(e.target.dataset.id, e.target.value);
    });
  });
}

// Función para abrir el modal con la imagen
function openImageModal(imageUrl) {
  const modal = document.getElementById('imageModal');
  const modalImg = document.getElementById('modalImage');
  modal.style.display = "block";
  modalImg.src = imageUrl;

  // Cerrar al hacer clic en la 'x'
  document.querySelector('.close').addEventListener('click', function() {
    modal.style.display = "none";
  });

  // Cerrar al hacer clic fuera de la imagen
  window.addEventListener('click', function(event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
}

async function updateAppointmentStatus(appointmentId, status) {
  try {
    const res = await fetch(`${API.updateAppointment}${appointmentId}`, {
      method: 'PUT',
      headers: {
        ...auth.headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status })
    });

    if (res.ok) {
      alert('Estado actualizado correctamente');
      loadDoctorAppointments();
    } else {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'Error actualizando estado');
    }
  } catch (err) {
    console.error('Error updating appointment:', err);
    alert(err.message);
  }
}

// ------------------ Inicialización del Dashboard Médico ------------------
document.addEventListener('DOMContentLoaded', async () => {
  auth.check();

  if (auth.role !== 'doctor') {
    alert('Acceso solo para médicos');
    auth.logout();
    return;
  }

  await fetchDoctorProfile();
  await loadDoctorAppointments();

  document.getElementById('logout-btn').addEventListener('click', auth.logout);

  // Inicializar el modal
  const modal = document.getElementById('imageModal');
  const closeBtn = document.querySelector('.close');

  closeBtn.addEventListener('click', function() {
    modal.style.display = "none";
  });

  window.addEventListener('click', function(event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
});
