"""Configuration file for gunicorn."""
# pylint: skip-file

bind = ["0.0.0.0:8000"]
threads = 1
workers = 3
timeout = 6000
worker_class = "uvicorn.workers.UvicornWorker"
