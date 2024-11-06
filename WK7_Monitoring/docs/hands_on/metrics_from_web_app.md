# WK7 Monitoring Hands-on
The source code of this hands-on experiment located at `WK7_Monitoring/code`.

## II.Prometheus on Docker

The Prometheus monitoring system differs from most other similar software in at least one key way. Instead of the application pushing metrics to the monitoring system, Prometheus scrapes the application via HTTP, usually on the `/metrics` endpoint.

### Step 0.(Optional) remove old docker images
First, stop and delete all existing containers and images:
```
docker stop $(docker ps -a -q)
docker rm $(docker ps -aq)
docker rmi -f $(docker images -a -q)
```
Also, remove the volumes:
```
docker volume prune
```
If you have run docker-compose up and would like to update the volume, please run:
```
docker compose down -v
```
### Step 1. Build and run a flask app
Now, build the new image:
```
cd code
docker build -t jr/flask_app .
```
Check the docker image 
```
docker image ls
```
Run it and verify it works:
```
docker run  -ti -p 3001:3001 jr/flask_app
```
Try to access `http://localhost:3001/green`. You should see Green.

Now, stop the Docker container by typing `ctrl+c` (or `command+c` for Mac).
### Step 2. Spin up the infrastructure

Now, let's spin up the app with our infrastructure setup: Prometheus, Grafana, StatsD and the Flask app.
```
docker compose -f docker-compose.yml -f docker-compose-infra.yml up
```

If any of the ports are already in use, change the service port in the Dockerfile and docker-compose files, or kill the existing process:
```
lsof -t -i tcp:1234 | xargs kill
```

#### Check Prometheus and StatsD

Hit some the below endpoints randomly 
- `http://localhost:3001/green` 
- `http://localhost:3001/red`
- `http://localhost:3001/simulation`

All the metrics available for the webapp can be found in `http://localhost:3001/metrics`, while all the metrics available for statsd can be found in `http://localhost:9102/metrics`
  
Next, let's run couple of queries in prometheus at `http://localhost:9090/graph`

```
request_count
```
To return the 5-minute rate of the http_requests_total metric for the past 30 minutes, with a resolution of 1 minute:
```
rate(request_count[5m])
```

The demo app also emits a custom metric `request_count_no_statsd_total`. Try searching the metrics a couple of times and check the value.

You may wonder why the request count returns inconsistent values. This is because the demo app is using a uWSGI server with 5 different processes, and there is no aggregator for it. Remember, we scrape the `/metrics` endpoint, which makes distinguishing between processes harder.

Try to report the last minute average request duration and P90 latency for different endpoints.

Hints:

```
rate(flask_http_request_duration_seconds_sum[1m])/rate(flask_http_request_duration_seconds_count[5m])
```
and 
```
histogram_quantile(0.9, sum by (le, path) (rate(flask_http_request_duration_seconds_bucket[5m])))
```

Lets' return the average request duration for the simulation endpoint only

Hints:

```
rate(flask_http_request_duration_seconds_sum{path="/simulation"}[5m])/rate(flask_http_request_duration_seconds_count{path="/simulation"}[5m])
```

Notes: If you see `NaN` in the result, it means there is no data in the selected time period. Please try hitting the endpoints a couple of more times.


### Step 3. Clean up

Now, lets remove all containers

```
docker compose -f docker-compose.yml -f docker-compose-infra.yml down
```

