from flask import Flask, request, jsonify, render_template
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
with sqlite3.connect(DB_PATH) as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS transactions
               (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, amount REAL, person TEXT, timestamp TEXT)''')


def parse_sms_data(data, time):
    value = {}
    data = data.split("\n")

    if data[0].startswith("Sent"):
        value["type"] = 'debit'
        value['amount'] = float(".".join(data[0].split(".")[-2:]))
        value['person'] = " ".join(data[2].split(" ")[1:])

    elif data[0].startswith("Credit"): 
        value["type"] = 'credit'
        value['amount'] = float(".".join(data[1].split()[0].split(".")[-2:]))
        value['person'] = data[1].split()[-3]
    value['timestamp'] = time

    return value


@app.route('/sms', methods=['POST'])
def receive_sms():
    data = request.json
    text = data.get('text', 'Unknown')
    time = data.get('time', 'Unknown')
    values = parse_sms_data(text, time)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO transactions (type, amount, person, timestamp) VALUES (?, ?, ?, ?)",
                    (values['type'], values['amount'], values['person'], values['timestamp']))
    

    return jsonify({"status": "logged"}), 200


@app.route('/')
def index():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT type, amount, person, timestamp FROM transactions")
        transactions = cur.fetchall()

    totalDebit = 0
    totalCredit = 0
    for i in range(len(transactions)):
        if transactions[i][0] == 'debit':
            totalDebit+=transactions[i][1]
        else:
            totalCredit+=transactions[i][1]
            
    return render_template('index.html', transactions=transactions, totalDebit=totalDebit, totalCredit=totalCredit)

"""if __name__ == '__main__':
    app.run(port=5000, debug=True)"""