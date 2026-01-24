# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import time
from flask import request, g
from functools import wraps
from .logger import generate_correlation_id, get_logger, sanitize_data

CORRELATION_ID_HEADER = 'X-Correlation-ID'


def request_logging_middleware(app, logger=None):
    if logger is None:
        logger = get_logger()
    
    @app.before_request
    def before_request():
        correlation_id = request.headers.get(CORRELATION_ID_HEADER) or generate_correlation_id()
        g.correlation_id = correlation_id
        g.start_time = time.time()
        
        logger.info(f'Incoming request: {request.method} {request.path} - user_agent={request.headers.get("User-Agent")} ip={request.remote_addr}')
        
        if request.is_json and request.get_json(silent=True):
            sanitized_body = sanitize_data(request.get_json())
            logger.debug(f'Request body: {sanitized_body}')
    
    @app.after_request
    def after_request(response):
        correlation_id = getattr(g, 'correlation_id', None)
        if correlation_id:
            response.headers[CORRELATION_ID_HEADER] = correlation_id
        
        duration = time.time() - getattr(g, 'start_time', time.time())
        duration_ms = round(duration * 1000, 2)
        
        logger.info(f'Request completed: {request.method} {request.path} - status={response.status_code} duration={duration_ms}ms')
        
        return response
    
    return app
