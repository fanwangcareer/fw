from flask import request
from datadog import DogStatsd
from prometheus_client import Counter
import time

# Initialize Datadog Statsd client
statsd = DogStatsd(host="statsd", port=9125)

# Define metric names for request latency and request count
REQUEST_LATENCY_METRIC_NAME = "request_latency_seconds_hist"
REQUEST_COUNT = "request_count"


def start_timer():
    # Start a timer at the beginning of the request
    request.start_time = time.time()


def stop_timer(response):
    # Calculate the request latency and send it to Datadog
    resp_time = time.time() - request.start_time
    statsd.histogram(
        REQUEST_LATENCY_METRIC_NAME,
        resp_time,
        tags=[
            "service:webapp",
            "endpoint:%s" % request.path,
            "method:%s" % request.method,
            "status:%s" % str(response.status_code),
        ],
    )
    return response


def record_request_data(response):
    # Increment the request count and send it to Datadog
    statsd.increment(
        REQUEST_COUNT,
        tags=[
            "service:webapp",
            "method:%s" % request.method,
            "endpoint:%s" % request.path,
            "status:%s" % str(response.status_code),
        ],
    )

def setup_metrics(app):
    # Register functions to be called before and after each request
    app.before_request(start_timer)
    # The order here matters since we want stop_timer to be executed first
    app.after_request(record_request_data)
    app.after_request(stop_timer)
