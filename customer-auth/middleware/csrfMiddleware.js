/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import crypto from 'crypto';

// CSRF token storage (in production, use Redis or database)
const csrfTokens = new Map();

// Token expiration time (1 hour)
const TOKEN_EXPIRY = 60 * 60 * 1000;

// Generate a CSRF token
const generateCsrfToken = () => crypto.randomBytes(32).toString('hex');

// Middleware to generate and set CSRF token
const csrfTokenGenerator = (req, res, next) => {
  // Generate a new token for each request
  const token = generateCsrfToken();
  const sessionId = req.cookies.sessionId || crypto.randomBytes(16).toString('hex');

  // Store token with expiration
  csrfTokens.set(sessionId, {
    token,
    expires: Date.now() + TOKEN_EXPIRY,
  });

  // Set session cookie if not exists
  if (!req.cookies.sessionId) {
    res.cookie('sessionId', sessionId, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: TOKEN_EXPIRY,
    });
  }

  // Set CSRF token in response header and cookie
  res.cookie('XSRF-TOKEN', token, {
    httpOnly: false, // Allow JavaScript to read this cookie
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: TOKEN_EXPIRY,
  });

  // Also set in response header for convenience
  res.setHeader('X-CSRF-Token', token);

  next();
};

// Middleware to validate CSRF token
const csrfProtection = (req, res, next) => {
  // Skip CSRF check for safe methods
  const safeMethods = ['GET', 'HEAD', 'OPTIONS'];
  if (safeMethods.includes(req.method)) {
    return next();
  }

  const { sessionId } = req.cookies;
  const tokenFromHeader = req.headers['x-csrf-token'] || req.headers['x-xsrf-token'];
  const tokenFromBody = req.body._csrf;
  const submittedToken = tokenFromHeader || tokenFromBody;

  if (!sessionId) {
    return res.status(403).json({
      message: 'CSRF validation failed: No session found',
    });
  }

  const storedData = csrfTokens.get(sessionId);

  if (!storedData) {
    return res.status(403).json({
      message: 'CSRF validation failed: Invalid session',
    });
  }

  // Check if token has expired
  if (Date.now() > storedData.expires) {
    csrfTokens.delete(sessionId);
    return res.status(403).json({
      message: 'CSRF validation failed: Token expired',
    });
  }

  // Validate token
  if (!submittedToken || submittedToken !== storedData.token) {
    return res.status(403).json({
      message: 'CSRF validation failed: Invalid token',
    });
  }

  // Token is valid, proceed
  next();
};

// Cleanup expired tokens periodically
setInterval(() => {
  const now = Date.now();
  for (const [sessionId, data] of csrfTokens.entries()) {
    if (now > data.expires) {
      csrfTokens.delete(sessionId);
    }
  }
}, 5 * 60 * 1000); // Clean up every 5 minutes

export { csrfTokenGenerator, csrfProtection, generateCsrfToken };
