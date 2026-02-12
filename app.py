from flask import Flask, request, jsonify
fr

app = Flask(__name__)

# This creates a text file in your cloud folder to save the SMS data
LOG_FILE = "sms_log.txt"

def parse_sms_data(data, time):
    value = {'time': time}
    data = data.split("\n")

    if data[0].startswith("Sent"): 
        value["type"] = 'debit'

    value['amount'] = float(data[0].split(" ")[-2]+data[0].split(" ")[-1])
    value['person'] = " ".join(data[0].split(" ")[1:])
    date = data[3].split(" ")[1]

    return value

@app.route('/')
def index():
    return "SMS Logger is running. Send POST requests to /sms to log messages."

@app.route('/sms', methods=['POST'])
def receive_sms():
    data = request.json
    text = data.get('text', 'Unknown')
    time = data.get('time', 'Unknown')
    
    
    with open(LOG_FILE, "a") as f:
        f.write(f"{parse_sms_data(text, time)}\n")
    
    return jsonify({"status": "logged"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)