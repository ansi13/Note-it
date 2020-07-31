import multiprocessing
import os
from pathlib import Path


# Create log & pid directory
LOG_FILE_PATH = './logs'
PID_FILE_PATH = './pids'


if os.path.isfile('.env'):
    with open('.env', 'r') as f:
        env_var = f.readlines()
else:
    env_var = []

try:
    Path.mkdir(Path(LOG_FILE_PATH), parents=True, exist_ok=True)
    Path.mkdir(Path(PID_FILE_PATH), parents=True, exist_ok=True)
except PermissionError:
    LOG_FILE_PATH = PID_FILE_PATH = "."

bind = '0.0.0.0:8000'
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 400
pidfile = f'{PID_FILE_PATH}/server.pid'
loglevel = 'debug'
raw_env = env_var
errorlog = f'{LOG_FILE_PATH}/server_error.log'
accesslog = f'{LOG_FILE_PATH}/server_access.log'
max_requests = 100
