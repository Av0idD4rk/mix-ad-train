document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);

  const res = await fetch("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: formData.get("email"),
      password: formData.get("password")
    })
  });

  const result = await res.json();
  if (res.ok) {
    alert("Registered successfully. You can now login.");
    window.location.href = "/static/login.html";
  } else {
    alert(result.detail || "Registration failed");
  }
});
