# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from enum import Enum
from flask import jsonify, g
import traceback
import os


class ErrorCodes(Enum):
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR'
    AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR'
    NOT_FOUND_ERROR = 'NOT_FOUND_ERROR'
    INTERNAL_ERROR = 'INTERNAL_ERROR'
    DATABASE_ERROR = 'DATABASE_ERROR'
    SERVICE_ERROR = 'SERVICE_ERROR'


class AppError(Exception):
    def __init__(self, message, status_code, error_code, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        self.is_operational = True


class ValidationError(AppError):
    def __init__(self, message, details=None):
        super().__init__(message, 400, ErrorCodes.VALIDATION_ERROR, details)


class AuthenticationError(AppError):
    def __init__(self, message='Authentication failed'):
        super().__init__(message, 401, ErrorCodes.AUTHENTICATION_ERROR)


class AuthorizationError(AppError):
    def __init__(self, message='Access denied'):
        super().__init__(message, 403, ErrorCodes.AUTHORIZATION_ERROR)


class NotFoundError(AppError):
    def __init__(self, message='Resource not found'):
        super().__init__(message, 404, ErrorCodes.NOT_FOUND_ERROR)


class InternalError(AppError):
    def __init__(self, message='Internal server error'):
        super().__init__(message, 500, ErrorCodes.INTERNAL_ERROR)


class DatabaseError(AppError):
    def __init__(self, message='Database operation failed'):
        super().__init__(message, 500, ErrorCodes.DATABASE_ERROR)


class ServiceError(AppError):
    def __init__(self, message='Service communication error'):
        super().__init__(message, 503, ErrorCodes.SERVICE_ERROR)


def create_error_response(error, correlation_id=None):
    if correlation_id is None:
        try:
            correlation_id = getattr(g, 'correlation_id', None)
        except RuntimeError:
            correlation_id = None
    
    if isinstance(error, AppError):
        response = {
            'success': False,
            'error': {
                'code': error.error_code.value,
                'message': error.message,
            },
            'correlationId': correlation_id,
        }
        if error.details:
            response['error']['details'] = error.details
        
        is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('NODE_ENV') == 'production'
        if not is_production:
            response['error']['stack'] = traceback.format_exc()
        
        return jsonify(response), error.status_code
    else:
        response = {
            'success': False,
            'error': {
                'code': ErrorCodes.INTERNAL_ERROR.value,
                'message': str(error) if str(error) else 'Internal server error',
            },
            'correlationId': correlation_id,
        }
        
        is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('NODE_ENV') == 'production'
        if not is_production:
            response['error']['stack'] = traceback.format_exc()
        
        return jsonify(response), 500


def register_error_handlers(app, logger):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        correlation_id = getattr(g, 'correlation_id', None)
        
        if error.is_operational:
            logger.warning(f'Operational error: {error.message}', 
                          error_code=error.error_code.value,
                          status_code=error.status_code)
        else:
            logger.error(f'Unhandled error: {error.message}',
                        error_code=error.error_code.value,
                        status_code=error.status_code)
        
        return create_error_response(error, correlation_id)
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        return create_error_response(ValidationError(str(error.description)))
    
    @app.errorhandler(401)
    def handle_unauthorized(error):
        return create_error_response(AuthenticationError(str(error.description)))
    
    @app.errorhandler(403)
    def handle_forbidden(error):
        return create_error_response(AuthorizationError(str(error.description)))
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return create_error_response(NotFoundError(str(error.description)))
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.error(f'Internal server error: {str(error)}')
        return create_error_response(InternalError())
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        logger.error(f'Unhandled exception: {str(error)}', exc_info=True)
        return create_error_response(error)
