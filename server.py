#!/usr/bin/env python3
"""
Simple HTTP server for DDoS testing
This server simulates a basic web application for testing your DDoS tool
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
import time
import threading
import psutil
import os
from datetime import datetime

app = Flask(__name__)

request_count = 0
start_time = time.time()
server_stats = {
    'requests_processed': 0,
    'bytes_sent': 0,
    'peak_memory': 0,
    'current_connections': 0
}

# Lock for thread-safe operations
stats_lock = threading.Lock()

LOG_FILE = "logs/server.log"


def log_message(message):
    """Log message to file with timestamp"""
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


@app.before_request
def before_request():
    """Track incoming requests"""
    global request_count
    with stats_lock:
        request_count += 1
        server_stats['requests_processed'] += 1
        server_stats['current_connections'] += 1

        # Update peak memory
        memory = psutil.virtual_memory().used
        if memory > server_stats['peak_memory']:
            server_stats['peak_memory'] = memory

    # Log request
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    log_message(f"REQUEST {request.method} {request.path} from {client_ip}")


@app.after_request
def after_request(response):
    """Track response statistics"""
    with stats_lock:
        server_stats['current_connections'] -= 1
        server_stats['bytes_sent'] += len(response.data)
    return response


@app.route('/')
def index():
    """Serve the main page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
            .stats { background-color: #e0e0e0; padding: 15px; margin-top: 20px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>DDoS Test Environment</h1>
            <p>This is a test server for validating DDoS penetration testing tools.</p>
        </div>

        <div class="stats">
            <h2>Server Information</h2>
            <p><strong>Status:</strong> Running</p>
            <p><strong>Uptime:</strong> <span id="uptime">0</span> seconds</p>
            <p><strong>Requests Processed:</strong> <span id="requests">0</span></p>
        </div>

        <script>
            // Update stats in real-time
            function updateStats() {
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('uptime').textContent = Math.floor(data.uptime);
                        document.getElementById('requests').textContent = data.requests_processed;
                    });
            }

            // Update stats every second
            setInterval(updateStats, 1000);
            updateStats(); // Initial call
        </script>
    </body>
    </html>
    """
    return html_content


@app.route('/api/stats')
def api_stats():
    """API endpoint for server statistics"""
    uptime = time.time() - start_time
    with stats_lock:
        stats = server_stats.copy()
    stats['uptime'] = uptime
    return jsonify(stats)


@app.route('/slow')
def slow_endpoint():
    """Simulate a slow endpoint that takes 2 seconds to respond"""
    time.sleep(2)
    return jsonify({
        "message": "Slow response completed",
        "processing_time": 2
    })


@app.route('/heavy')
def heavy_endpoint():
    """Simulate a CPU-intensive endpoint"""
    # Perform some CPU-intensive work
    result = 0
    for i in range(1000000):
        result += i * i

    return jsonify({
        "message": "Heavy computation completed",
        "result": result
    })


@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "status": "OK",
        "server": "DDoS Test Environment",
        "timestamp": time.time()
    })


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "uptime_seconds": time.time() - start_time,
        "requests_processed": server_stats['requests_processed']
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    log_message(f"404 NOT FOUND for {request.path}")
    return jsonify({
        "error": "Not found",
        "path": request.path
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    log_message(f"500 INTERNAL ERROR for {request.path}: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "path": request.path
    }), 500


def print_server_info():
    """Print server information"""
    print("=" * 50)
    print("DDoS Test Environment Server")
    print("=" * 50)
    print("Server starting...")
    print("Endpoints available:")
    print("  GET  /              - Main page")
    print("  GET  /api/stats     - Server statistics")
    print("  GET  /api/status    - API status")
    print("  GET  /health        - Health check")
    print("  GET  /slow          - Slow response (2 seconds)")
    print("  GET  /heavy         - CPU-intensive response")
    print("")
    print("Server will be available at:")
    print("  http://localhost:8000")
    print("  http://127.0.0.1:8000")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)


if __name__ == '__main__':
    os.makedirs("logs", exist_ok=True)
    open(LOG_FILE, "w").close()

    print_server_info()

    try:
        app.run(
            host='127.0.0.1',
            port=8000,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Server error: {e}")
