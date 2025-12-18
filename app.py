from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
from datetime import date

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Needed for flash messages

DATA_FILE = os.path.join('data', 'sleep_data.json')

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"goal": 8.0, "entries": []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    data = load_data()
    today_str = date.today().isoformat()
    return render_template('index.html', data=data, today=today_str)

@app.route('/add_sleep', methods=['POST'])
def add_sleep():
    data = load_data()
    sleep_date = request.form.get('sleep_date')
    hours_str = request.form.get('hours_slept')

    try:
        hours = float(hours_str)
        if hours <= 0:
            raise ValueError
    except (TypeError, ValueError):
        flash('Please enter a valid number of hours.', 'danger')
        return redirect(url_for('index'))

    # Update or add entry
    existing = next((e for e in data['entries'] if e['date'] == sleep_date), None)
    if existing:
        existing['slept'] = hours
        existing['achieved'] = hours >= data['goal']
        flash('Sleep entry updated!', 'success')
    else:
        data['entries'].append({
            'date': sleep_date,
            'slept': hours,
            'achieved': hours >= data['goal']
        })
        flash('Sleep entry added!', 'success')

    save_data(data)
    return redirect(url_for('index'))

@app.route('/goal')
def goal():
    data = load_data()
    return render_template('goal.html', data=data)

@app.route('/set_goal', methods=['POST'])
def set_goal():
    data = load_data()
    goal_str = request.form.get('goal_hours')

    try:
        goal = float(goal_str)
        if goal <= 0:
            raise ValueError
    except (TypeError, ValueError):
        flash('Please enter a valid goal in hours.', 'danger')
        return redirect(url_for('goal'))

    data['goal'] = goal
    # Update all achievements based on new goal
    for entry in data['entries']:
        entry['achieved'] = entry['slept'] >= goal

    save_data(data)
    flash('Sleep goal updated successfully!', 'success')
    return redirect(url_for('goal'))

if __name__ == '__main__':
    # For local development
    app.run(debug=True)
