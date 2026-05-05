from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest

app = Flask(__name__)

REQUEST_COUNT = Counter(
    'app_request_count',
    'Total request count',
    ['endpoint']
)

@app.route('/')
def home():
    REQUEST_COUNT.labels(endpoint='/').inc()
    return jsonify({
        "message": "Hello from DevOps Project!",
        "status": "running"
    })

@app.route('/health')
def health():
    REQUEST_COUNT.labels(endpoint='/health').inc()
    return jsonify({"status": "healthy"})

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)