# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import datetime
import openai
import os

app = Flask(__name__)

# ---------- CONFIG ----------
# Load your OpenAI key (set this in your environment first)
openai.api_key = os.getenv("your_api_key_here")

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect("patients.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            condition TEXT,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


# ---------- Routes ----------
@app.route("/")
def index():
    conn = sqlite3.connect("patients.db")
    c = conn.cursor()
    c.execute("SELECT * FROM patients ORDER BY id DESC")
    patients = c.fetchall()
    conn.close()
    return render_template("index.html", patients=patients)

@app.route("/add", methods=["POST"])
def add_patient():
    name = request.form["name"]
    age = request.form["age"]
    condition = request.form["condition"]
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    conn = sqlite3.connect("patients.db")
    c = conn.cursor()
    c.execute("INSERT INTO patients (name, age, condition, date) VALUES (?, ?, ?, ?)",
              (name, age, condition, date))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# ---------- AI Chatbot ----------
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful medical assistant. Keep responses short and clear."},
                      {"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)
