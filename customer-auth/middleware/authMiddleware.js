/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import jwt from 'jsonwebtoken';
import asyncHandler from 'express-async-handler';
import User from '../models/userModel.js';

// Middleware to protect routes - verifies JWT token
const protect = asyncHandler(async (req, res, next) => {
  let token;

  // Check for token in Authorization header (Bearer token)
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    token = req.headers.authorization.split(' ')[1];
  }
  // Also check for token in cookies
  else if (req.cookies && req.cookies.jwt) {
    token = req.cookies.jwt;
  }
  // Fallback to raw authorization header (backward compatibility)
  else if (req.headers.authorization) {
    token = req.headers.authorization;
  }

  if (token) {
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);

      // Check if token is an access token
      if (decoded.type && decoded.type !== 'access') {
        res.status(401);
        throw new Error('Invalid token type');
      }

      req.user = await User.findById(decoded.userId).select('-password');

      if (!req.user) {
        res.status(401);
        throw new Error('User not found');
      }

      // Attach role from token to request
      req.userRole = decoded.role || req.user.role || 'customer';

      next();
    } catch (error) {
      console.error(error);
      res.status(401);
      throw new Error('Not authorized, token failed or expired');
    }
  } else {
    res.status(401);
    throw new Error('Not authorized, no token');
  }
});

// Middleware for role-based authorization
const authorize = (...roles) => (req, res, next) => {
  if (!req.user) {
    res.status(401);
    throw new Error('Not authorized');
  }

  const userRole = req.userRole || req.user.role || 'customer';

  if (!roles.includes(userRole)) {
    res.status(403);
    throw new Error(`Role '${userRole}' is not authorized to access this resource`);
  }

  next();
};

export { protect, authorize };
