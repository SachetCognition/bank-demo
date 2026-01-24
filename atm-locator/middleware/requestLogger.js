/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import { generateCorrelationId, createChildLogger, sanitizeData } from '../utils/logger.js';

const CORRELATION_ID_HEADER = 'x-correlation-id';

export const requestLogger = (req, res, next) => {
  const correlationId = req.headers[CORRELATION_ID_HEADER] || generateCorrelationId();
  req.correlationId = correlationId;
  req.logger = createChildLogger(correlationId);

  res.setHeader(CORRELATION_ID_HEADER, correlationId);

  const startTime = Date.now();

  req.logger.info('Incoming request', {
    method: req.method,
    url: req.originalUrl,
    userAgent: req.get('user-agent'),
    ip: req.ip || req.connection.remoteAddress,
  });

  if (req.body && Object.keys(req.body).length > 0) {
    req.logger.debug('Request body', { body: sanitizeData(req.body) });
  }

  const originalSend = res.send;
  res.send = function (body) {
    const duration = Date.now() - startTime;
    
    req.logger.info('Request completed', {
      method: req.method,
      url: req.originalUrl,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
    });

    return originalSend.call(this, body);
  };

  next();
};

export default requestLogger;
