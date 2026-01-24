# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import logging
import sys
import os
import uuid
import json
from datetime import datetime
from functools import wraps
from flask import request, g

SERVICE_NAME = os.getenv('SERVICE_NAME', 'dashboard')
SERVICE_VERSION = os.getenv('SERVICE_VERSION', '1.0.0')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

SENSITIVE_FIELDS = {'password', 'token', 'jwt', 'secret', 'authorization', 'cookie', 'api_key'}


class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'service': SERVICE_NAME,
            'version': SERVICE_VERSION,
            'message': record.getMessage(),
            'logger': record.name,
        }
        
        if hasattr(record, 'correlation_id'):
            log_record['correlation_id'] = record.correlation_id
        
        if hasattr(record, 'extra_data') and record.extra_data:
            log_record['metadata'] = record.extra_data
        
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        if os.getenv('NODE_ENV') == 'production' or os.getenv('FLASK_ENV') == 'production':
            return json.dumps(log_record)
        else:
            correlation_id = log_record.get('correlation_id', 'N/A')
            metadata = log_record.get('metadata', '')
            if metadata:
                metadata = f" {json.dumps(metadata)}"
            exc = ''
            if 'exception' in log_record:
                exc = f"\n{log_record['exception']}"
            return f"{log_record['timestamp']} [{record.levelname}] [{correlation_id}] {record.getMessage()}{metadata}{exc}"


class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        try:
            record.correlation_id = getattr(g, 'correlation_id', 'N/A')
        except RuntimeError:
            record.correlation_id = 'N/A'
        return True


def setup_logger(name=None, level=None):
    logger = logging.getLogger(name or SERVICE_NAME)
    logger.setLevel(getattr(logging, level or LOG_LEVEL))
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        handler.addFilter(CorrelationIdFilter())
        logger.addHandler(handler)
    
    return logger


def get_logger(name=None):
    return setup_logger(name)


def generate_correlation_id():
    return str(uuid.uuid4())


def sanitize_data(data):
    if data is None:
        return data
    
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_FIELDS:
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, (dict, list)):
                sanitized[key] = sanitize_data(value)
            else:
                sanitized[key] = value
        return sanitized
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    
    return data


def log_with_context(logger, level, message, **kwargs):
    extra_data = sanitize_data(kwargs) if kwargs else None
    record = logger.makeRecord(
        logger.name, 
        getattr(logging, level.upper()), 
        '', 0, message, (), None
    )
    record.extra_data = extra_data
    logger.handle(record)


logger = setup_logger()
