
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import random

app = Flask(__name__)

DATA_FILE = "participants.json"

def load_participants():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_participants(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@app.route("/")
def index():
    participants = load_participants()
    return render_template("index.html", participants=participants)

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name")
    if not name:
        return redirect(url_for("index"))
    participants = load_participants()
    if name not in participants:
        participants.append(name)
    save_participants(participants)
    return redirect(url_for("index"))

@app.route("/clear")
def clear():
    save_participants([])
    return redirect(url_for("index"))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
