
from flask import Flask, render_template, request, redirect, url_for
import os
import json
import random

app = Flask(__name__)

def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return default

def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    participants = load_json("participants.json", [])
    archive = load_json("archive.json", [])
    groups = load_json("groups.json", {})
    history = load_json("history.json", [])
    return render_template("index.html", participants=participants, archive=archive, groups=groups, history=history)

@app.route("/add", methods=["POST"])
def add():
    names = request.form.get("names", "").splitlines()
    participants = load_json("participants.json", [])
    for name in names:
        name = name.strip()
        if name and name not in participants:
            participants.append(name)
    save_json(participants, "participants.json")
    return redirect(url_for("index"))

@app.route("/clear")
def clear():
    save_json([], "participants.json")
    save_json({}, "groups.json")
    return redirect(url_for("index"))

@app.route("/archive")
def archive():
    participants = load_json("participants.json", [])
    archive = load_json("archive.json", [])
    for p in participants:
        if p not in archive:
            archive.append(p)
    save_json(archive, "archive.json")
    return redirect(url_for("index"))

@app.route("/autogroup", methods=["POST"])
def autogroup():
    num_groups = int(request.form.get("num_groups", 2))
    stage = request.form.get("stage", "Квалификация 1")
    group_labels = ["A", "B", "C", "D", "E", "F", "G", "H"]

    participants = load_json("participants.json", [])
    history = load_json("history.json", [])
    used_numbers = {p['name']: p.get('numbers', []) for p in history}
    random.shuffle(participants)

    groups = {}
    for i in range(num_groups):
        groups[group_labels[i]] = []

    for idx, name in enumerate(participants):
        group = group_labels[idx % num_groups]
        group_size = len(groups[group])
        existing = used_numbers.get(name, [])
        new_number = random.choice([n for n in range(1, len(participants)+1) if n not in existing])
        groups[group].append({"name": name, "number": new_number})

    # Обновляем историю
    for group_name, members in groups.items():
        for m in members:
            entry = next((item for item in history if item["name"] == m["name"]), None)
            if entry:
                entry["numbers"].append(m["number"])
            else:
                history.append({"name": m["name"], "numbers": [m["number"]]})

    save_json(groups, "groups.json")
    save_json(history, "history.json")
    return redirect(url_for("index"))
