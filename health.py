from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    # You can add more comprehensive health checks here if needed
    # For example, you might check the status of a database connection
    # For simplicity, let's assume the application is always healthy
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True)