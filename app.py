from flask import Flask, render_template, request, redirect, jsonify
import json, os, random

app = Flask(__name__)

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    participants = load_json("participants.json", [])
    archive = load_json("archive.json", [])
    groups = load_json("groups.json", {})
    history = load_json("history.json", [])
    return render_template("index.html", participants=participants, archive=archive, groups=groups)

@app.route("/add", methods=["POST"])
def add():
    names = request.form.get("names", "").splitlines()
    participants = load_json("participants.json", [])
    for name in names:
        name = name.strip()
        if name and name not in participants:
            participants.append(name)
    save_json("participants.json", participants)
    return redirect("/")

@app.route("/clear")
def clear():
    save_json("participants.json", [])
    save_json("groups.json", {})
    return redirect("/")

@app.route("/archive")
def archive():
    participants = load_json("participants.json", [])
    archive = load_json("archive.json", [])
    for p in participants:
        if p not in archive:
            archive.append(p)
    save_json("archive.json", archive)
    return redirect("/")

@app.route("/autogroup", methods=["POST"])
def autogroup():
    num_groups = int(request.form.get("num_groups", 2))
    stage = request.form.get("stage", "Квалификация 1")
    group_labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    participants = load_json("participants.json", [])
    history = load_json("history.json", [])
    used_numbers = {h['name']: h.get('numbers', []) for h in history}
    random.shuffle(participants)

    groups = {group_labels[i]: [] for i in range(num_groups)}
    for i, name in enumerate(participants):
        group = group_labels[i % num_groups]
        group_size = len(groups[group])
        pool = list(set(range(1, group_size + 20)) - set(used_numbers.get(name, [])))
        number = random.choice(pool) if pool else random.randint(1, 99)
        groups[group].append({"name": name, "number": number})
        entry = next((h for h in history if h['name'] == name), None)
        if entry:
            if number not in entry["numbers"]:
                entry["numbers"].append(number)
        else:
            history.append({"name": name, "numbers": [number]})

    save_json("groups.json", groups)
    save_json("history.json", history)
    return redirect("/")

@app.route("/save_groups", methods=["POST"])
def save_groups():
    data = request.get_json()
    save_json("groups.json", data)
    return jsonify(success=True)
