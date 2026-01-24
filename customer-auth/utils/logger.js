/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import winston from 'winston';
import { v4 as uuidv4 } from 'uuid';

const {
  combine, timestamp, printf, colorize, errors,
} = winston.format;

const SERVICE_NAME = 'customer-auth';
const SERVICE_VERSION = process.env.SERVICE_VERSION || '1.0.0';

const logFormat = printf(({
  level, message, timestamp, correlationId, service, ...metadata
}) => {
  const log = {
    timestamp,
    level,
    service: service || SERVICE_NAME,
    version: SERVICE_VERSION,
    correlationId: correlationId || 'N/A',
    message,
  };

  if (Object.keys(metadata).length > 0) {
    log.metadata = metadata;
  }

  return JSON.stringify(log);
});

const consoleFormat = printf(({
  level, message, timestamp, correlationId, ...metadata
}) => {
  let metaStr = '';
  if (Object.keys(metadata).length > 0 && metadata.stack === undefined) {
    metaStr = ` ${JSON.stringify(metadata)}`;
  }
  if (metadata.stack) {
    metaStr = `\n${metadata.stack}`;
  }
  return `${timestamp} [${level}] [${correlationId || 'N/A'}] ${message}${metaStr}`;
});

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: combine(
    timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
    errors({ stack: true }),
    logFormat,
  ),
  defaultMeta: { service: SERVICE_NAME },
  transports: [
    new winston.transports.Console({
      format: combine(
        colorize(),
        timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
        errors({ stack: true }),
        process.env.NODE_ENV === 'production' ? logFormat : consoleFormat,
      ),
    }),
  ],
});

export const generateCorrelationId = () => uuidv4();

export const createChildLogger = (correlationId) => logger.child({ correlationId });

export const sanitizeData = (data) => {
  if (!data) return data;

  const sensitiveFields = ['password', 'token', 'jwt', 'secret', 'authorization', 'cookie'];
  const sanitized = { ...data };

  for (const field of sensitiveFields) {
    if (sanitized[field]) {
      sanitized[field] = '[REDACTED]';
    }
  }

  return sanitized;
};

export default logger;
