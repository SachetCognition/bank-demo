/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

// API Key authentication middleware for service-to-service communication

// Get API key from environment variable
const INTERNAL_API_KEY = process.env.INTERNAL_API_KEY || 'martianbank-internal-api-key-change-in-production';

// Middleware to validate API key for internal service calls
const validateApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'] || req.headers['x-internal-api-key'];

  // If no API key is provided, check if request is from internal network
  // In production, you would check the source IP or use service mesh
  if (!apiKey) {
    // Allow requests without API key for now (backward compatibility)
    // In production, you should require API key for all internal calls
    return next();
  }

  // Validate the API key
  if (apiKey !== INTERNAL_API_KEY) {
    return res.status(401).json({
      message: 'Invalid API key',
    });
  }

  // Mark request as internal service call
  req.isInternalCall = true;
  next();
};

// Middleware to require API key (stricter version)
const requireApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'] || req.headers['x-internal-api-key'];

  if (!apiKey) {
    return res.status(401).json({
      message: 'API key required for this endpoint',
    });
  }

  if (apiKey !== INTERNAL_API_KEY) {
    return res.status(401).json({
      message: 'Invalid API key',
    });
  }

  req.isInternalCall = true;
  next();
};

// Helper function to add API key to outgoing requests
const getApiKeyHeader = () => ({
  'X-Internal-API-Key': INTERNAL_API_KEY,
});

export {
  validateApiKey, requireApiKey, getApiKeyHeader, INTERNAL_API_KEY,
};
