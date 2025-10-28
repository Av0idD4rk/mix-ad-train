const form = document.getElementById('premiumForm');
const msg = document.getElementById('msg');

if (!localStorage.getItem('token')) {
    window.location.href = '/login.html';
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    msg.textContent = '';

    const token = localStorage.getItem("token");
    const res = await fetch('/premium/buy', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
            key: formData.get('key'),
        }),
    });
    const result = await res.json();
    if (res.ok) {
        localStorage.setItem("token", result.access_token);
        msg.textContent = 'Поздравляем, вы успешно приобрели премиум подписку!';
    } else {
      msg.textContent = res.detail || 'Неверный премиум ключ';
      return;
    }
});
