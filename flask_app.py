from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

conn = sqlite3.connect('database.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS transactions
               (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, amount REAL, person TEXT, timestamp DATETIME)''')
conn.close()

LOG_FILE = "sms_log.txt"

def parse_sms_data(data, time):
    value = {}
    data = data.split("\n")

    if data[0].startswith("Sent"): value["type"] = 'debit'
    elif data[0].startswith("Credit"): value["type"] = 'credit'

    value['amount'] = float(".".join(data[0].split(".")[-2:]))
    value['person'] = " ".join(data[2].split(" ")[1:])
    date = data[3].split(" ")[1]
    value['timestamp'] = time

    return value

@app.route('/')
def index():
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
    return render_template('index.html', values=lines)

@app.route('/sms', methods=['POST'])
def receive_sms():
    conn = sqlite3.connect('database.db')
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