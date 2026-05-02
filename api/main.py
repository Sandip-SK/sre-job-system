from fastapi import FastAPI
from redis import Redis
from rq import Queue
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response
import time

app = FastAPI()
redis_conn = Redis(host='redis', port=6379)
q = Queue(connection=redis_conn)

# Metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests")
REQUEST_LATENCY = Histogram("http_request_latency_seconds", "Request latency")

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    REQUEST_COUNT.inc()
    REQUEST_LATENCY.observe(time.time() - start_time)
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

@app.get("/")
def root():
    return {"message": "API is running"}

@app.post("/task")
def create_task():
    job = q.enqueue("tasks.process_task")
    return {"job_id": job.id}

@app.get("/health")
def health():
    return {"status": "ok"}