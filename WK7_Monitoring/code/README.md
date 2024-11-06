# Flask Application Monitoring Demo

This project demonstrates how to implement comprehensive monitoring and logging for a Flask application using both Datadog and Prometheus. It showcases various monitoring aspects including HTTP requests, system metrics, and PostgreSQL database monitoring.

## Architecture Overview

The project consists of the following components:

- **Flask Application**: A Python web application instrumented for monitoring
- **PostgreSQL Database**: Backend database with monitoring enabled
- **Prometheus**: Open-source monitoring and alerting system
- **StatsD**: For collecting custom metrics
- **Grafana**: Dashboarding and visualization tools for Prometheus metrics
- **Datadog Agent**: For collecting and forwarding metrics to Datadog
- **Node Exporter**: For system-level metrics
- **PostgreSQL Exporter**: For database-specific metrics

### Monitoring Stack

#### Prometheus Monitoring
- HTTP request metrics using `prometheus_flask_exporter`
- System metrics via Node Exporter
- PostgreSQL metrics via postgres_exporter
- Custom application metrics

#### Grafana Dashboard
- Data source integration with Prometheus
- Custom dashboards for application-specific metrics
- Real-time monitoring and visualization
- Alerting and notification configuration

#### Datadog Monitoring
- Flask application performance monitoring
- Database monitoring
- System metrics
- Custom metrics and traces

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- PostgreSQL
- Datadog account (for Datadog integration)

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/australiaitgroup/DevOpsNotes.git
cd WK7_Monitoring/code
```

2. Build the Flask application image:
```bash
docker build -t jr/flask_app .
```

3. Environment Configuration:
   - Copy `.env.example` to `.env`
   - Update the following variables:
     ```
     DD_API_KEY=your_datadog_api_key
     ```

4. Start all services
```bash
docker-compose -f docker-compose.yml -f docker-compose-infra.yml up -d
```

5. Access Flask application at `http://localhost:3001`

## Code Structure and Implementation Details

#### docker-compose.yml
This file defines the Flask web application service configuration:
- Uses custom image `jr/flask_app`
- Exposes port 3001
- Configures Datadog integration through labels
- Sets environment variables for:
  - Datadog service configuration
  - Database connection parameters
  - Application versioning

#### docker-compose-infra.yml
Defines the monitoring infrastructure:
- **Prometheus Stack**:
  - Prometheus server (port 9090)
  - Node Exporter (port 9100)
  - StatsD Exporter (ports 9102, 9125)
  - PostgreSQL Exporter (port 9187)
- **Grafana** (port 3000)
- **PostgreSQL** (port 5432)
- **Datadog Agent**:
  - APM enabled
  - Log collection configured
  - PostgreSQL integration

### Application Code

#### Dockerfile
- Uses Python 3.12.4 slim base image
- Installs necessary system dependencies
- Sets up application directory
- Uses uWSGI as the application server with:
  - 5 worker processes
  - Threading enabled
  - HTTP port 3001

#### flask_app.py
Main application file implementing:

1. **Monitoring Integration**:
- Prometheus metrics
  ```python
  from prometheus_flask_exporter import PrometheusMetrics
  metrics = PrometheusMetrics(app)
  metrics.info("app_info", "Application info", version="1.0.3")
  ```
- Datadog tracing
  ```python
    from ddtrace import tracer, patch
    patch(flask=True)
    tracer.configure(hostname='datadog', port=8126)
  ```
2. **Database Connectivity**:
   ```python
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
    ```
3. **Request Logging**:
  ```python
  def log_request(endpoint, status_code, message=""):
    # Logs requests to PostgreSQL database
  ```
  * Writing log to database is purely for demonstration purposes. In a production environment, you would typically log to a dedicated logging service or file.

#### app_helper.py
1. **Metric Recording**:
  ```python
  def record_request_data(response):
    statsd.increment(
        REQUEST_COUNT,
        tags=[...]
    )
  ```
2. **Request Timing**:
  ```python
  def start_timer():
    request.start_time = time.time()

  def stop_timer(response):
    resp_time = time.time() - request.start_time
    statsd.histogram(...)
  ```

## Monitoring Component Details

### Flask Application
- Located in `app/`
- Instrumented with both Prometheus and Datadog metrics
- Includes example endpoints demonstrating different monitoring scenarios

### Application Monitoring
- Prometheus metrics:
  - HTTP request counts
  - Response times
  - Application version
- Datadog APM:
  - Distributed tracing
  - Request latency
  - Error tracking

### Database Monitoring
- PostgreSQL metrics exposed via postgres_exporter
- Datadog PostgreSQL integration enabled
- Key metrics monitored:
  - Query performance
  - Connection pools
  - Database size
  - Transaction rates

### System Monitoring
- Node Exporter metrics:
  - CPU usage
  - Memory utilization
  - Disk I/O
  - Network statistics

## Monitoring Implementation Details

### Prometheus Metrics
- **Application Metrics**: 
  - Request counts
  - Response times
  - Application info
- **System Metrics**: 
  - CPU, Memory, Disk usage via Node Exporter
- **Database Metrics**: 
  - Connection pools
  - Query statistics
  - Transaction rates

### Datadog Integration
- **APM (Application Performance Monitoring)**:
  - Distributed tracing
  - Request latency
  - Error tracking
- **Custom Metrics**:
  - Request counts via StatsD
  - Response time histograms
- **Database Monitoring**:
  - PostgreSQL performance metrics
  - Query analysis
  - Connection pooling stats

## Usage Examples

### Testing the Application

```bash
# Test endpoints
curl http://localhost:3001/
curl http://localhost:3001/green
curl http://localhost:3001/red
curl http://localhost:3001/simulation

# View Prometheus metrics
curl http://localhost:3001/metrics
```

### Access Monitoring Components

### Prometheus Metrics
   - Flask App Metrics: `http://localhost:3001/metrics`
   - StatsD: `http://localhost:9102/metrics`
   - Node Exporter: `http://localhost:9100/metrics`
   - PostgreSQL Exporter: `http://localhost:9187/metrics`
   - Prometheus: `http://localhost:9090`
   - Grafana: `http://localhost:3000`
     - Username: admin
     - Password: foobar
   - Datadog: `https://app.datadoghq.com/apm/home`

### Datadog Metrics
- Access via Datadog dashboard
- Default metrics available under:
  - `trace.flask.*`
  - `postgresql.*`
  - `system.*`

## Example Queries

### Prometheus PromQL Examples
```promql
# HTTP Request Rate
rate(flask_http_request_total[5m])

# Database Connections
pg_stat_activity_count

# System Load Average
node_load1
```

### Datadog Query Examples
```
# Flask Request Latency
avg:flask.request.duration{*}

# Database Connections
avg:postgresql.connections{*}
```

## Troubleshooting

1. Verify services are running:
```bash
docker-compose ps
```

2. Check logs:
```bash
docker-compose logs -f [service_name]
```

3. Common issues:
   - Ensure all ports are available
   - Verify Datadog API key is correct
   - Check PostgreSQL credentials
