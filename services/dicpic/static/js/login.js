document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);

  const res = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: formData.get("email"),
      password: formData.get("password")
    })
  });

  const result = await res.json();
  if (res.ok) {
    localStorage.setItem("token", result.access_token);
    window.location.href = "/static/index.html";
  } else {
    alert(result.detail || "Login failed");
  }
});
