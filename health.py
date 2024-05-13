from flask import Flask, jsonify
from logger import LoggingMiddleware

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    app.run(debug=True, port=8000)()