from flask import Flask, request, jsonify, session
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load env
load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "supersecretkey"  # for session handling

@app.route("/")
def home():
    return "Task Manager API is running"

# DB connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# ---------------- USER AUTH ----------------

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = generate_password_hash(data.get("password"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400

    cursor.close()
    conn.close()
    return jsonify({"message": "User created successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["id"]
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully"})


# ---------------- TASKS ----------------

@app.route("/tasks", methods=["GET"])
def get_tasks():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE user_id=%s ORDER BY created_at DESC", (session["user_id"],))
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, completed, user_id) VALUES (%s, %s, %s)",
        (data["title"], False, session["user_id"])
    )
    conn.commit()
    task_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id": task_id, "title": data["title"], "completed": False})


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    title = data.get("title")
    completed = data.get("completed")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET title=%s, completed=%s WHERE id=%s AND user_id=%s",
        (title, completed, task_id, session["user_id"]),
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Task updated successfully"})


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s AND user_id=%s", (task_id, session["user_id"]))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Task deleted successfully"})


if __name__ == "__main__":
    app.run(debug=True)
