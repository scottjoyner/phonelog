bind = "0.0.0.0:8000"
workers = 2
threads = 4
timeout = 60
graceful_timeout = 30
loglevel = "info"


# Prometheus multiprocess cleanup
try:
    from prometheus_client import multiprocess
    def child_exit(server, worker):
        multiprocess.mark_process_dead(worker.pid)
except Exception:
    pass
