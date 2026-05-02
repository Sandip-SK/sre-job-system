# SRE Job System

A distributed job processing system built with Python, Redis, and Kubernetes. This system consists of an API server that accepts job requests and a worker service that processes jobs asynchronously.

## 📋 Table of Contents

- [Architecture](#architecture)
- [Components](#components)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [Local Development with Docker Compose](#local-development-with-docker-compose)
  - [Kubernetes Deployment](#kubernetes-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      SRE Job System                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   Client     │         │   Monitoring │                  │
│  │   Request    │         │  (Prometheus)│                  │
│  └──────────────┘         └──────────────┘                  │
│         │                         │                          │
│         ▼                         ▼                          │
│  ┌──────────────────────────────────────┐                   │
│  │      Task API (Port 8080)            │                   │
│  │  - Accepts job submissions           │                   │
│  │  - Exposes metrics                   │                   │
│  └──────────────────────────────────────┘                   │
│         │                                                    │
│         │ enqueue jobs                                       │
│         ▼                                                    │
│  ┌──────────────────────────────────────┐                   │
│  │      Redis (Port 6379)               │                   │
│  │  - Job queue storage                 │                   │
│  │  - Result cache                      │                   │
│  └──────────────────────────────────────┘                   │
│         ▲                                                    │
│         │ get jobs, store results                            │
│         │                                                    │
│  ┌──────────────────────────────────────┐                   │
│  │    Worker Process (Background)       │                   │
│  │  - Polls Redis for jobs              │                   │
│  │  - Processes tasks                   │                   │
│  │  - Reports metrics                   │                   │
│  └──────────────────────────────────────┘                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
   Client                API                Redis              Worker
     │                   │                   │                   │
     │  POST /jobs       │                   │                   │
     ├──────────────────>│                   │                   │
     │                   │                   │                   │
     │              Job Created              │                   │
     │<──────────────────┤                   │                   │
     │              Job ID returned          │                   │
     │                   │                   │                   │
     │                   │  ENQUEUE job      │                   │
     │                   ├──────────────────>│                   │
     │                   │                   │                   │
     │                   │                   │ DEQUEUE job       │
     │                   │                   │<──────────────────┤
     │                   │                   │  Process job      │
     │                   │                   │  (background)     │
     │                   │                   │                   │
     │  GET /jobs/{id}   │                   │                   │
     ├──────────────────>│                   │                   │
     │                   │  GET result       │                   │
     │                   ├──────────────────>│                   │
     │                   │<──────────────────┤                   │
     │<──────────────────┤                   │                   │
     │  Job status/result                    │                   │
```

## 🔧 Components

### 1. **Task API Server** (`api/`)
- **Language**: Python (Flask/FastAPI)
- **Port**: 8080
- **Responsibilities**:
  - Accept job submission requests
  - Store jobs in Redis queue
  - Retrieve job status and results
  - Expose Prometheus metrics

**Key Environment Variables**:
- `REDIS_HOST`: Redis service hostname (default: "redis")
- `REDIS_PORT`: Redis service port (default: 6379)

### 2. **Worker Process** (`worker/`)
- **Language**: Python
- **Responsibilities**:
  - Poll Redis for pending jobs
  - Execute tasks asynchronously
  - Store results back in Redis
  - Report metrics and health status

**Key Environment Variables**:
- `REDIS_HOST`: Redis service hostname (default: "redis")
- `REDIS_PORT`: Redis service port (default: 6379)

### 3. **Redis** 
- **Port**: 6379
- **Role**: 
  - Central message broker for job queue
  - Result cache
  - State storage
- **Kubernetes Image**: `redis:7`

### 4. **Monitoring Stack** (`monitoring/`)
- **Prometheus**: Metrics collection and storage
- **AlertManager**: Alert routing and management
- **Metrics Scraped**: Task processing metrics, Redis stats, HTTP metrics

## 📁 Project Structure

```
sre-job-system/
├── api/
│   ├── main.py              # Flask/FastAPI application
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile           # Container image definition
│   └── .dockerignore
├── worker/
│   ├── worker.py            # Worker process main script
│   ├── tasks.py             # Task processing logic
│   ├── __init__.py
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile           # Container image definition
│   └── .dockerignore
├── k8s/
│   ├── api-deployment.yaml      # API Kubernetes deployment
│   ├── api-service.yaml         # API service (NodePort 30007)
│   ├── redis-deployment.yaml    # Redis deployment
│   ├── redis-service.yaml       # Redis service (ClusterIP 6379)
│   └── worker-deployment.yml    # Worker deployment
├── monitoring/
│   ├── prometheus.yml           # Prometheus scrape config
│   ├── alerts.yml               # Alerting rules
│   ├── alertmanager.yml         # AlertManager config
├── docker-compose.yml       # Local development stack
└── README.md               # This file
```

## 🚀 Quick Start

### Local Development with Docker Compose

#### Prerequisites
- Docker and Docker Compose installed
- Git

#### Steps

1. **Clone and navigate to project**:
   ```bash
   cd sre-job-system
   ```

2. **Build containers**:
   ```bash
   docker-compose build
   ```

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

4. **Verify services are running**:
   ```bash
   docker-compose ps
   ```

5. **Test the API**:
   ```bash
   # Submit a job
   curl -X POST http://localhost:8080/jobs \
     -H "Content-Type: application/json" \
     -d '{"task": "process_data", "params": {"key": "value"}}'
   
   # Get job status
   curl http://localhost:8080/jobs/{job_id}
   ```

6. **View logs**:
   ```bash
   docker-compose logs -f api      # API logs
   docker-compose logs -f worker   # Worker logs
   docker-compose logs -f redis    # Redis logs
   ```

7. **Stop services**:
   ```bash
   docker-compose down
   ```

---

### Kubernetes Deployment

#### Prerequisites
- Kubernetes cluster (1.20+)
- `kubectl` configured to access your cluster
- Container images pushed to registry (Docker Hub in this case: `sandy10/mini-sre-api:1.0`)

#### Deployment Steps

1. **Create namespace (optional)**:
   ```bash
   kubectl create namespace sre-jobs
   ```

2. **Deploy Redis**:
   ```bash
   kubectl apply -f k8s/redis-deployment.yaml
   kubectl apply -f k8s/redis-service.yaml
   ```

3. **Deploy API**:
   ```bash
   kubectl apply -f k8s/api-deployment.yaml
   kubectl apply -f k8s/api-service.yaml
   ```

4. **Deploy Worker**:
   ```bash
   kubectl apply -f k8s/worker-deployment.yml
   ```

5. **Verify deployment**:
   ```bash
   kubectl get pods
   kubectl get services
   ```

6. **Access the API**:
   ```bash
   # Get node IP
   kubectl get nodes -o wide
   
   # API accessible at: http://<node-ip>:30007
   curl http://<node-ip>:30007/jobs
   ```

7. **View logs**:
   ```bash
   kubectl logs -f deployment/task-api
   kubectl logs -f deployment/worker
   kubectl logs -f deployment/redis
   ```

8. **Scale workers**:
   ```bash
   kubectl scale deployment worker --replicas=3
   ```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `REDIS_HOST` | API, Worker | `redis` | Redis hostname |
| `REDIS_PORT` | API, Worker | `6379` | Redis port |
| `API_PORT` | API | `8080` | API server port |
| `WORKER_CONCURRENCY` | Worker | `4` | Number of concurrent jobs |
| `JOB_TIMEOUT` | Worker | `300` | Job timeout in seconds |

### Resource Limits (Kubernetes)

**API Pod**:
- Requests: 250m CPU, 64Mi memory
- Limits: 500m CPU, 128Mi memory

**Worker Pod**:
- Consider adding similar resource limits
- Scale replicas for better throughput

**Redis Pod**:
- Single replica (consider using Redis Sentinel for HA)

## 📊 Monitoring

### Prometheus Metrics

The system exposes the following metrics:

```
# API Metrics
http_requests_total              # Total HTTP requests
http_request_duration_seconds    # Request latency
jobs_submitted_total             # Total jobs submitted
jobs_completed_total             # Total jobs completed
jobs_failed_total                # Total failed jobs

# Worker Metrics
worker_jobs_processed_total      # Jobs processed by worker
worker_job_duration_seconds      # Job processing duration
worker_errors_total              # Worker errors

# Redis Metrics
redis_connected_clients          # Connected clients
redis_used_memory_bytes          # Memory usage
redis_keyspace_hits              # Cache hits
```

### Access Prometheus

- **Local**: `http://localhost:9090`
- **Kubernetes**: Port-forward to Prometheus pod

### Alerts

Configured alerts in `monitoring/alerts.yml`:
- High error rate
- Worker pod down
- Redis memory usage high
- API response time high

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Worker not processing jobs
- **Check Redis connection**: `redis-cli -h redis ping`
- **Check worker logs**: `docker-compose logs worker`
- **Verify REDIS_HOST environment variable**

#### 2. API returns 500 errors
- **Check API logs**: `docker-compose logs api`
- **Verify Redis is running**: `docker-compose ps redis`
- **Check API dependencies**: `pip list` in API container

#### 3. High memory usage
- **Check Redis memory**: `redis-cli info memory`
- **Scale workers**: `kubectl scale deployment worker --replicas=5`
- **Review job complexity**: Consider breaking large jobs into smaller tasks

#### 4. Jobs stuck in queue
- **Check worker replica count**: `kubectl get deployment worker`
- **Inspect Redis directly**: `redis-cli`
  ```
  LLEN job_queue          # Queue length
  HGETALL job_{id}        # Job details
  ```

### Health Checks

```bash
# API health
curl http://localhost:8080/health

# Worker status
curl http://localhost:8080/worker-status

# Redis connectivity
redis-cli -h redis ping
```

---

## 📝 Development

### Adding New Task Types

1. **Define task in `worker/tasks.py`**:
   ```python
   def process_custom_task(params):
       # Implementation
       return result
   ```

2. **Submit job via API**:
   ```bash
   curl -X POST http://localhost:8080/jobs \
     -d '{"task_type": "custom_task", "params": {...}}'
   ```

### Building Custom Images

```bash
# Build API image
docker build -t your-registry/api:latest api/

# Build Worker image
docker build -t your-registry/worker:latest worker/

# Push to registry
docker push your-registry/api:latest
docker push your-registry/worker:latest
```
---

**Last Updated**: May 2, 2026
