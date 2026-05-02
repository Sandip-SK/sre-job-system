from prometheus_client import Counter, Histogram
import time

JOB_COUNT = Counter("jobs_processed_total", "Total jobs processed")
JOB_DURATION = Histogram("job_duration_seconds", "Job duration")

def process_task():
    start = time.time()

    print("Processing task...")
    time.sleep(5)

    JOB_COUNT.inc()
    JOB_DURATION.observe(time.time() - start)

    print("Task completed")
    return "done"