let accessToken = "";

function register() {
  const data = {
    username: document.getElementById("reg-username").value,
    password: document.getElementById("reg-password").value,
    name: document.getElementById("reg-name").value,
    age: parseInt(document.getElementById("reg-age").value),
  };

  fetch("/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((res) => res.json())
    .then((res) => alert(JSON.stringify(res)));
}

function login() {
  const data = {
    username: document.getElementById("login-username").value,
    password: document.getElementById("login-password").value,
  };

  fetch("/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((res) => res.json())
    .then((res) => {
      accessToken = res.access_token;
      alert("로그인 성공! accessToken 저장됨!");
    });
}

function getProfile() {
  fetch("/api/profile", {
    method: "GET",
    headers: {
      Authorization: "Bearer " + accessToken,
    },
  })
    .then((res) => res.json())
    .then((res) => {
      document.getElementById("profile-result").innerText = JSON.stringify(res);
    });
}
