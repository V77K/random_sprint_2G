
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import random

app = Flask(__name__)

DATA_FILE = "participants.json"
ARCHIVE_FILE = "archive.json"
GROUPS_FILE = "groups.json"

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return []

def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    participants = load_json(DATA_FILE)
    archive = load_json(ARCHIVE_FILE)
    groups = load_json(GROUPS_FILE)
    return render_template("index.html", participants=participants, archive=archive, groups=groups)

@app.route("/add", methods=["POST"])
def add():
    names = request.form.get("names", "").splitlines()
    participants = load_json(DATA_FILE)
    for name in names:
        name = name.strip()
        if name and name not in participants:
            participants.append(name)
    save_json(participants, DATA_FILE)
    return redirect(url_for("index"))

@app.route("/clear")
def clear():
    save_json([], DATA_FILE)
    save_json({}, GROUPS_FILE)
    return redirect(url_for("index"))

@app.route("/archive")
def archive():
    participants = load_json(DATA_FILE)
    archive = load_json(ARCHIVE_FILE)
    for p in participants:
        if p not in archive:
            archive.append(p)
    save_json(archive, ARCHIVE_FILE)
    return redirect(url_for("index"))

@app.route("/autogroup")
def autogroup():
    participants = load_json(DATA_FILE)
    random.shuffle(participants)
    num_groups = int(request.args.get("num_groups", 2))
    group_labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
    result = {}
    for i in range(num_groups):
        result[group_labels[i]] = []
    for idx, name in enumerate(participants):
        group = group_labels[idx % num_groups]
        result[group].append({"name": name, "number": idx+1})
    save_json(result, GROUPS_FILE)
    return redirect(url_for("index"))
