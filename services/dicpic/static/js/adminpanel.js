const msg = document.getElementById('msg');
const usersContainer = document.getElementById('usersContainer');
const serverCheckForm = document.getElementById('serverCheckForm');
const serverCheckResult = document.getElementById('serverCheckResult');
const logoutBtn = document.getElementById('logoutBtn');

const token = localStorage.getItem('admin_token');

if (!token) {
  window.location.href = '/static/adminlogin.html';
}

const headers = {
  'Authorization': `Bearer ${token}`
};

function renderTable(data, columns, container) {
  if (!data.length) {
    container.innerHTML = '<p>Данных нет.</p>';
    return;
  }
  let html = '<table><thead><tr>';
  columns.forEach(col => {
    html += `<th>${col}</th>`;
  });
  html += '</tr></thead><tbody>';
  data.forEach(row => {
    html += '<tr>';
    columns.forEach(col => {
      html += `<td>${row[col]}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  container.innerHTML = html;
}

async function loadUsers() {
  msg.textContent = '';
  usersContainer.innerHTML = 'Загрузка...';
  try {
    const res = await fetch('/admin/users', { headers });
    if (!res.ok) {
      const err = await res.json();
      msg.textContent = err.detail || 'Ошибка при загрузке пользователей';
      usersContainer.innerHTML = '';
      return;
    }
    const data = await res.json();
    renderTable(data, ['id', 'email', 'password', 'is_premium'], usersContainer);
  } catch (e) {
    msg.textContent = 'Ошибка сети';
    usersContainer.innerHTML = '';
  }
}

document.getElementById('loadUsersBtn').addEventListener('click', loadUsers);

logoutBtn.addEventListener('click', () => {
  localStorage.removeItem('admin_token');
  window.location.href = '/static/adminlogin.html';
});
