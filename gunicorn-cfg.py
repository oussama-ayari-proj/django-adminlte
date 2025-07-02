# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

bind = '0.0.0.0:5005'
workers = 1
accesslog = '-'
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True

# File upload settings
max_requests = 1000
max_requests_jitter = 100
timeout = 120
keepalive = 5

# Increase worker memory and request limits for file uploads
worker_class = 'sync'
worker_connections = 1000
limit_request_line = 8190
limit_request_fields = 200
limit_request_field_size = 16384
