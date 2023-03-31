from multiprocessing import cpu_count

# Socket Path
bind = 'unix:/tmp/gunicorn.sock'

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = '/home/gcpuser/access_log'
errorlog =  '/home/gcpuser/error_log'
from multiprocessing import cpu_count

# Socket Path
bind = 'unix:/tmp/gunicorn.sock'

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = '/home/gcpuser/access_log'
errorlog =  '/home/gcpuser/error_log'

forwarded_allow_ips = "127.0.0.1,[::1]"
proxy_protocol = True
proxy_allow_from = "*"
