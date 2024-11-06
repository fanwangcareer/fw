from flask import Flask, request, g
import random
import os
import time
import psycopg2
from prometheus_flask_exporter import PrometheusMetrics
from datetime import datetime
import logging

# Datadog tracing imports
from ddtrace import tracer, patch

# Apply the Flask patch
patch(flask=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tracer configuration
tracer.configure(hostname='datadog', port=8126)

DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "changeme")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")

# Create Flask application
app = Flask(__name__)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Define a static information metric for the application
metrics.info("app_info", "Application info", version="1.0.3")

# Function to get database connection
def get_db_connection():
    if 'conn' not in g:
        try:
            g.conn = psycopg2.connect(
                dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            logger.info("Database connection established.")
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            g.conn = None
    return g.conn

# Function to log request details to PostgreSQL
def log_request(endpoint, status_code, message=""):
    conn = get_db_connection()
    if conn is None:
        logger.warning("Database connection not available for logging.")
        return

    try:
        with conn.cursor() as cursor:
            query = """
                INSERT INTO request_log (timestamp, source_ip, endpoint, status_code, message)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    datetime.now(),
                    request.remote_addr,
                    endpoint,
                    status_code,
                    message
                )
            )
            conn.commit()
            logger.info(f"Logged request to {endpoint} with status {status_code}")
    except Exception as e:
        logger.error(f"Error logging to database: {e}")
        conn.rollback()

# Define the '/' route handler
@app.route("/")
def hello_world():
    log_request("/", 200, "Hello World endpoint hit.")
    return "JR Demo App!"

# Define the '/green' route handler
@app.route("/green")
def green():
    log_request("/green", 200, "Green endpoint hit.")
    return "Green"

# Define the '/red' route handler
@app.route("/red")
def red():
    try:
        1 / 0  # This will cause a division by zero error
    except Exception as e:
        log_request("/red", 500, f"Error: {e}")
        logger.exception("Exception occurred in /red endpoint")
        return "Red", 500
    return "Red"

# Configure simulation request error rate and latency range
ERROR_RATE = 0.1  # 10% chance of error
LATENCY_MIN = 100  # Minimum latency in milliseconds
LATENCY_MAX = 1000  # Maximum latency in milliseconds

# Define the '/simulation' route handler
@app.route("/simulation")
def simulation():
    # Simulate variable response latency
    latency_ms = random.uniform(LATENCY_MIN, LATENCY_MAX)
    time.sleep(latency_ms / 1000.0)

    if random.random() < ERROR_RATE:
        # Simulate an error
        try:
            raise Exception("Simulated error based on configured error rate.")
        except Exception as e:
            log_request("/simulation", 500, f"Simulated error: {e}")
            logger.exception("Simulated exception in /simulation endpoint")
            return str(e), 500

    log_request("/simulation", 200, f"Simulated latency: {latency_ms:.2f} ms")
    logger.info(f"Simulation request successful with latency {latency_ms:.2f} ms")
    return f"Request successful. Simulated latency: {latency_ms:.2f} milliseconds."

# Define error handler to handle 500 errors
@app.errorhandler(500)
def handle_500(error):
    log_request(request.path, 500, str(error))
    logger.error(f"500 Error on {request.path}: {error}")
    return str(error), 500

# Ensure the database connection is properly closed per request
@app.teardown_appcontext
def close_connection(exception):
    conn = g.pop('conn', None)
    if conn is not None:
        conn.close()
        logger.info("Database connection closed.")

# Run Flask application
if __name__ == "__main__":
    app.run(debug=True)
