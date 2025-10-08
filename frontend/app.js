const API_URL = "http://127.0.0.1:5000";
let loggedIn = false;

/* ---------------- AUTH FUNCTIONS ---------------- */

function signup() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  fetch(`${API_URL}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password }),
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById("authMessage").innerText = data.message || data.error;
    });
}

function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password }),
  })
    .then(res => res.json())
    .then(data => {
      if (data.message) {
        loggedIn = true;
        document.getElementById("authMessage").innerText = "✅ Logged in!";
        document.getElementById("taskSection").style.display = "block";
        loadTasks();
      } else {
        document.getElementById("authMessage").innerText = data.error;
      }
    });
}

function logout() {
  fetch(`${API_URL}/logout`, {
    method: "POST",
    credentials: "include",
  }).then(() => {
    loggedIn = false;
    document.getElementById("authMessage").innerText = "🚪 Logged out!";
    document.getElementById("taskSection").style.display = "none";
  });
}

/* ---------------- TASK FUNCTIONS ---------------- */

function loadTasks() {
  fetch(`${API_URL}/tasks`, { credentials: "include" })
    .then(res => res.json())
    .then(tasks => {
      const tbody = document.getElementById("taskTableBody");
      tbody.innerHTML = "";
      tasks.forEach(task => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td style="${task.completed ? "text-decoration: line-through;" : ""}">
            ${task.title}
          </td>
          <td>
            <input type="checkbox" ${task.completed ? "checked" : ""} 
              onchange="toggleComplete(${task.id}, '${task.title}', this.checked)">
          </td>
          <td>
            <button onclick="updateTask(${task.id}, '${task.title}', ${task.completed})">✏️</button>
            <button onclick="deleteTask(${task.id})">🗑️</button>
          </td>
        `;
        tbody.appendChild(row);
      });
    });
}

document.getElementById("addTaskBtn").addEventListener("click", () => {
  const title = prompt("Enter task:");
  if (title) {
    fetch(`${API_URL}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include", // 🔥 required for session
      body: JSON.stringify({ title }),
    }).then(() => loadTasks());
  }
});

function updateTask(id, oldTitle, completed) {
  const newTitle = prompt("Update task:", oldTitle);
  if (newTitle) {
    fetch(`${API_URL}/tasks/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ title: newTitle, completed }),
    }).then(() => loadTasks());
  }
}

function deleteTask(id) {
  if (confirm("Are you sure you want to delete this task?")) {
    fetch(`${API_URL}/tasks/${id}`, {
      method: "DELETE",
      credentials: "include",
    }).then(() => loadTasks());
  }
}

function toggleComplete(id, title, completed) {
  fetch(`${API_URL}/tasks/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ title, completed }),
  }).then(() => loadTasks());
}
