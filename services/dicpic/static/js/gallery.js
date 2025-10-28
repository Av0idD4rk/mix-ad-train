function getUserIdFromToken() {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.sub;
  } catch (e) {
    console.error("Ошибка разбора токена:", e);
    return null;
  }
}

async function loadPhotos() {
  const token = localStorage.getItem("token");
  const isPremiumUser = localStorage.getItem("is_premium") === "true";

  const res = await fetch("/photo/all_files", {
    headers: { Authorization: `Bearer ${token}` }
  });

  const photosDiv = document.getElementById("photos");
  photosDiv.innerHTML = "";

  if (!res.ok) {
    const err = await res.json();
    photosDiv.innerHTML = `<p class="error-message">Ошибка: ${err.detail}</p>`;
    return;
  }

  const result = await res.json();

  if (result.length === 0) {
    photosDiv.innerHTML = "<p>Фото не найдены.</p>";
    return;
  }

  renderPhotos(result, isPremiumUser);
}

function renderPhotos(photos, isPremiumUser) {
  const photosDiv = document.getElementById("photos");
  photosDiv.innerHTML = "";

  const currentUserId = getUserIdFromToken();

  photos.forEach(p => {
    const card = document.createElement("div");
    card.classList.add("photo-card");

    const isAuthor = String(p.author_id) === String(currentUserId);
    const shouldHide = p.premium_only && !isPremiumUser && !isAuthor && !p.file_base64;

    if (shouldHide) {
      card.innerHTML = `
        <div class="image-wrapper locked-premium">
          <div class="premium-label">Только для премиум</div>
        </div>
      `;
    } else {
      const title = `<h3>${p.name}</h3>`;
      const desc = `<p>${p.description}</p>`;
      const imgSrc = p.file_base64 || "/static/img/placeholder.png";

      const image = `
        <div class="image-wrapper">
          <img src="${imgSrc}" alt="${p.name}" />
        </div>
      `;

      card.innerHTML = title + desc + image;
    }

    photosDiv.appendChild(card);
  });
}

async function searchPhotos() {
  const query = document.getElementById("searchInput").value.trim();
  const token = localStorage.getItem("token");
  const isPremiumUser = localStorage.getItem("is_premium") === "true";

  if (!query) {
    loadPhotos();
    return;
  }

  const res = await fetch(`/photo/search?q=${encodeURIComponent(query)}`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const photosDiv = document.getElementById("photos");
  photosDiv.innerHTML = "";

  if (!res.ok) {
    const err = await res.json();
    photosDiv.innerHTML = `<p class="error-message">Ошибка: ${err.detail}</p>`;
    return;
  }

  const result = await res.json();

  if (result.length === 0) {
    photosDiv.innerHTML = "<p>Ничего не найдено.</p>";
    return;
  }

  renderPhotos(result, isPremiumUser);
}

document.getElementById("uploadForm").addEventListener("submit", async e => {
  e.preventDefault();

  const token = localStorage.getItem("token");
  const formData = new FormData(e.target);

  const res = await fetch("/photo/upload", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData
  });

  if (!res.ok) {
    const err = await res.json();
    alert("Ошибка загрузки: " + err.detail);
    return;
  }

  alert("Фото успешно загружено!");
  e.target.reset();
  loadPhotos();
});

document.getElementById("searchButton").addEventListener("click", searchPhotos);
document.getElementById("clearButton").addEventListener("click", () => {
  document.getElementById("searchInput").value = "";
  loadPhotos();
});

window.addEventListener("DOMContentLoaded", loadPhotos);
