/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import express from 'express';
import mongoose from 'mongoose';
import logger from '../utils/logger.js';

const router = express.Router();

const SERVICE_NAME = 'customer-auth';
const SERVICE_VERSION = process.env.SERVICE_VERSION || '1.0.0';

const getDbStatus = () => {
  const state = mongoose.connection.readyState;
  const states = {
    0: 'disconnected',
    1: 'connected',
    2: 'connecting',
    3: 'disconnecting',
  };
  return {
    status: state === 1 ? 'healthy' : 'unhealthy',
    state: states[state] || 'unknown',
  };
};

router.get('/health', (req, res) => {
  const dbStatus = getDbStatus();
  const isHealthy = dbStatus.status === 'healthy';

  const healthResponse = {
    status: isHealthy ? 'healthy' : 'unhealthy',
    service: SERVICE_NAME,
    version: SERVICE_VERSION,
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    checks: {
      database: dbStatus,
    },
  };

  if (!isHealthy) {
    logger.warn('Health check failed', { checks: healthResponse.checks });
  }

  res.status(isHealthy ? 200 : 503).json(healthResponse);
});

router.get('/health/live', (req, res) => {
  res.status(200).json({
    status: 'alive',
    service: SERVICE_NAME,
    timestamp: new Date().toISOString(),
  });
});

router.get('/health/ready', (req, res) => {
  const dbStatus = getDbStatus();
  const isReady = dbStatus.status === 'healthy';

  res.status(isReady ? 200 : 503).json({
    status: isReady ? 'ready' : 'not_ready',
    service: SERVICE_NAME,
    timestamp: new Date().toISOString(),
    checks: {
      database: dbStatus,
    },
  });
});

export default router;
