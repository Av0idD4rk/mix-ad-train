const form = document.getElementById('loginForm');
const msg = document.getElementById('msg');

if (localStorage.getItem('admin_token')) {
  window.location.href = '/adminpanel.html';
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  msg.textContent = '';

  const data = {
    username: form.username.value.trim(),
    password: form.password.value.trim(),
  };

  try {
    const res = await fetch('/admin/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const error = await res.json();
      msg.textContent = error.detail || 'Неверные данные';
      return;
    }
    const json = await res.json();
    localStorage.setItem('admin_token', json.admin_token);
    window.location.href = '/static/adminpanel.html';
  } catch (e) {
    msg.textContent = 'Ошибка сети';
  }
});
