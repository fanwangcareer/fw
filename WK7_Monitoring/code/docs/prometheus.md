### Prometheus PromQL Examples

#### HTTP Metrics
```promql
# Request Rate by Endpoint
sum(rate(flask_http_request_total[5m])) by (endpoint)

# 95th Percentile Latency
histogram_quantile(0.95, sum(rate(flask_http_request_duration_seconds_bucket[5m])) by (le, endpoint))

# Error Rate
sum(rate(flask_http_request_total{status=~"5.."}[5m])) / sum(rate(flask_http_request_total[5m]))
```

#### System Metrics

```promql
# CPU Saturation
avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance)

# Memory Pressure
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes 100

# Disk I/O Pressure
rate(node_disk_io_time_seconds_total[5m]) 100

# Network Traffic
sum(rate(node_network_receive_bytes_total[5m])) by (device)
```
#### Database Metrics

```promql
# Active Connections
pg_stat_activity_count{state="active"}

# Transaction Rate
rate(pg_stat_database_xact_commit{datname="postgres"}[5m])

# Cache Hit Ratio
pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)

# Lock Waiting Queries
pg_stat_activity_count{state="waiting"}

#Query Execution Time
rate(pg_stat_statements_total_time_seconds[5m])
```