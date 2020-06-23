import multiprocessing

bind = '0.0.0.0:8000'
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 400
pidfile = 'server.pid'
loglevel = 'debug'
errorlog = 'server_error.log'
accesslog = 'server_access.log'
max_requests = 100