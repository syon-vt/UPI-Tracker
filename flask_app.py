from flask import Flask, request, jsonify, render_template
import sqlite3
import os

#BASE_DIR = "/home/Cracked/UPI-Tracker"
DB_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
with sqlite3.connect(DB_PATH) as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS transactions
               (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, amount REAL, person TEXT, timestamp TEXT)''')


def parse_sms_data(data, time):
    value = {}
    data = data.split("\n")

    if data[0].startswith("Sent"): value["type"] = 'debit'
    elif data[0].startswith("Credit"): value["type"] = 'credit'

    value['amount'] = float(".".join(data[0].split(".")[-2:]))
    value['person'] = " ".join(data[2].split(" ")[1:])
    value['timestamp'] = time

    return value


@app.route('/sms', methods=['POST'])
def receive_sms():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = request.json
    text = data.get('text', 'Unknown')
    time = data.get('time', 'Unknown')
    values = parse_sms_data(text, time)

    cur.execute("INSERT INTO transactions (type, amount, person, timestamp) VALUES (?, ?, ?, ?)",
                (values['type'], values['amount'], values['person'], values['timestamp']))
    conn.commit()
    conn.close()

    return jsonify({"status": "logged"}), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)