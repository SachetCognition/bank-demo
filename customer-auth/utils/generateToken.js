/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import jwt from 'jsonwebtoken';

// Access token expiration time (15 minutes)
const ACCESS_TOKEN_EXPIRY = '15m';
// Refresh token expiration time (7 days)
const REFRESH_TOKEN_EXPIRY = '7d';

// Generate access token (short-lived)
const generateAccessToken = (userId, role = 'customer') => jwt.sign(
  { userId, role, type: 'access' },
  process.env.JWT_SECRET,
  { expiresIn: ACCESS_TOKEN_EXPIRY },
);

// Generate refresh token (long-lived)
const generateRefreshToken = (userId) => jwt.sign(
  { userId, type: 'refresh' },
  process.env.JWT_REFRESH_SECRET || process.env.JWT_SECRET,
  { expiresIn: REFRESH_TOKEN_EXPIRY },
);

// Generate both tokens and return them
const generateTokens = (userId, role = 'customer') => {
  const accessToken = generateAccessToken(userId, role);
  const refreshToken = generateRefreshToken(userId);
  return { accessToken, refreshToken };
};

// Verify refresh token and generate new access token (token rotation)
const rotateTokens = (refreshToken) => {
  try {
    const decoded = jwt.verify(
      refreshToken,
      process.env.JWT_REFRESH_SECRET || process.env.JWT_SECRET,
    );

    if (decoded.type !== 'refresh') {
      throw new Error('Invalid token type');
    }

    // Generate new tokens (token rotation for security)
    return generateTokens(decoded.userId);
  } catch (error) {
    throw new Error('Invalid refresh token');
  }
};

// Legacy function for backward compatibility
const generateToken = (res, userId, role = 'customer') => {
  const { accessToken, refreshToken } = generateTokens(userId, role);

  // Set access token cookie
  res.cookie('jwt', accessToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 15 * 60 * 1000, // 15 minutes
  });

  // Set refresh token cookie
  res.cookie('refreshToken', refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
  });

  return { accessToken, refreshToken };
};

export default generateToken;
export {
  generateAccessToken,
  generateRefreshToken,
  generateTokens,
  rotateTokens,
  ACCESS_TOKEN_EXPIRY,
  REFRESH_TOKEN_EXPIRY,
};
