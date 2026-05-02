import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from redis import Redis
from rq import Worker, Queue
import tasks

# NEW: Prometheus HTTP server
from prometheus_client import start_http_server

redis_conn = Redis(host="redis", port=6379)

if __name__ == "__main__":
    # Start metrics server on port 8001
    start_http_server(8001)

    worker = Worker([Queue(connection=redis_conn)], connection=redis_conn)
    worker.work()