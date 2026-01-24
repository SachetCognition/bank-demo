/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import logger from '../utils/logger.js';
import { AppError, ErrorCodes, NotFoundError } from '../utils/errors.js';

const notFound = (req, res, next) => {
  const error = new NotFoundError(`Not Found - ${req.originalUrl}`);
  next(error);
};

const errorHandler = (err, req, res, next) => {
  const reqLogger = req.logger || logger;
  
  let statusCode = err.statusCode || (res.statusCode === 200 ? 500 : res.statusCode);
  let errorCode = err.errorCode || ErrorCodes.INTERNAL_ERROR;
  let { message } = err;

  if (err.name === "CastError" && err.kind === "ObjectId") {
    statusCode = 404;
    errorCode = ErrorCodes.NOT_FOUND_ERROR;
    message = "Resource not found";
  }

  if (err.name === "ValidationError") {
    statusCode = 400;
    errorCode = ErrorCodes.VALIDATION_ERROR;
  }

  if (err.name === "MongoError" || err.name === "MongoServerError") {
    statusCode = 500;
    errorCode = ErrorCodes.DATABASE_ERROR;
    message = "Database operation failed";
  }

  const isOperational = err instanceof AppError && err.isOperational;
  
  if (!isOperational) {
    reqLogger.error('Unhandled error occurred', {
      error: message,
      stack: err.stack,
      errorCode,
      statusCode,
      url: req.originalUrl,
      method: req.method,
    });
  } else {
    reqLogger.warn('Operational error occurred', {
      error: message,
      errorCode,
      statusCode,
      url: req.originalUrl,
      method: req.method,
    });
  }

  const response = {
    success: false,
    error: {
      code: errorCode,
      message,
      ...(err.details && { details: err.details }),
    },
    correlationId: req.correlationId || null,
  };

  if (process.env.NODE_ENV !== "production") {
    response.error.stack = err.stack;
  }

  res.status(statusCode).json(response);
};

export { notFound, errorHandler };
