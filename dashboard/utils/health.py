# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import os
import time
from flask import Blueprint, jsonify
from pymongo.mongo_client import MongoClient
from .logger import get_logger

START_TIME = time.time()

def create_health_blueprint(service_name, db_client=None):
    health_bp = Blueprint('health', __name__)
    logger = get_logger(service_name)
    service_version = os.getenv('SERVICE_VERSION', '1.0.0')
    
    def check_database():
        if db_client is None:
            return {'status': 'unknown', 'state': 'not_configured'}
        
        try:
            db_client.admin.command('ping')
            return {'status': 'healthy', 'state': 'connected'}
        except Exception as e:
            logger.error(f'Database health check failed: {str(e)}')
            return {'status': 'unhealthy', 'state': 'disconnected'}
    
    @health_bp.route('/health', methods=['GET'])
    def health():
        db_status = check_database()
        is_healthy = db_status['status'] == 'healthy' or db_status['state'] == 'not_configured'
        
        health_response = {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'service': service_name,
            'version': service_version,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'uptime': round(time.time() - START_TIME, 2),
            'checks': {
                'database': db_status,
            },
        }
        
        if not is_healthy:
            logger.warning('Health check failed', checks=health_response['checks'])
        
        return jsonify(health_response), 200 if is_healthy else 503
    
    @health_bp.route('/health/live', methods=['GET'])
    def liveness():
        return jsonify({
            'status': 'alive',
            'service': service_name,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        }), 200
    
    @health_bp.route('/health/ready', methods=['GET'])
    def readiness():
        db_status = check_database()
        is_ready = db_status['status'] == 'healthy' or db_status['state'] == 'not_configured'
        
        return jsonify({
            'status': 'ready' if is_ready else 'not_ready',
            'service': service_name,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'checks': {
                'database': db_status,
            },
        }), 200 if is_ready else 503
    
    return health_bp
