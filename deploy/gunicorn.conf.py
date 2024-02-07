bind = "0.0.0.0:80"

worker_class = "uvicorn.workers.UvicornWorker"

workers = 2
threads = 2

accesslog = "-"
