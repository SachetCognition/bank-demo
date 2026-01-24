/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import asyncHandler from 'express-async-handler';
import User from '../models/userModel.js';
import logger from '../utils/logger.js';
import { ValidationError, NotFoundError, AuthenticationError } from '../utils/errors.js';

// @desc    Register a new user
// @route   POST /api/users
// @access  Public
const registerUser = asyncHandler(async (req, res, next) => {
  const reqLogger = req.logger || logger;

  const { name, email, password } = req.body;

  if (!name || !email || !password) {
    return next(new ValidationError('Name, email and password are required'));
  }

  const userExists = await User.findOne({ email });

  if (userExists) {
    return next(new ValidationError('User already exists'));
  }

  const user = await User.create({
    name,
    email,
    password,
  });

  if (user) {
    reqLogger.info('User registered successfully', { userId: user._id, email: user.email });
    res.status(201).json({
      _id: user._id,
      name: user.name,
      email: user.email,
    });
  } else {
    return next(new ValidationError('Invalid user data'));
  }
});

// @desc    Auth user & get token
// @route   POST /api/users/auth
// @access  Public
const authUser = asyncHandler(async (req, res, next) => {
  const reqLogger = req.logger || logger;

  const { email, password } = req.body;

  if (!email || !password) {
    return next(new ValidationError('Email and password are required'));
  }

  const user = await User.findOne({ email });

  if (user && (await user.matchPassword(password))) {
    reqLogger.info('User authenticated successfully', { userId: user._id, email: user.email });
    res.json({
      _id: user._id,
      name: user.name,
      email: user.email,
    });
  } else {
    reqLogger.warn('Authentication failed', { email });
    return next(new AuthenticationError('Invalid email or password'));
  }
});

// @desc    Logout user and clear cookie
// @route   POST /api/users/logout
// @access  Public
const logoutUser = (req, res) => {
  const reqLogger = req.logger || logger;
  reqLogger.info('User logged out');
  res.status(200).json({ message: 'Logged out successfully' });
};

// @desc    Get user profile
// @route   POST api/users/profile
// @access  Private
const getUserProfile = asyncHandler(async (req, res, next) => {
  const reqLogger = req.logger || logger;
  const user = await User.findOne({ email: req.body.email });

  if (user) {
    reqLogger.info('User profile retrieved', { userId: user._id });
    res.json({
      _id: user._id,
      name: user.name,
      email: user.email,
    });
  } else {
    return next(new NotFoundError('User not found'));
  }
});

// @desc    Update user profile
// @route   PUT /api/users/profile
// @access  Private
const updateUserProfile = asyncHandler(async (req, res, next) => {
  const reqLogger = req.logger || logger;
  const user = await User.findOne({ email: req.body.email });

  if (user) {
    user.password = req.body.password || user.password;

    const updatedUser = await user.save();

    reqLogger.info('User profile updated', { userId: updatedUser._id });
    res.json({
      _id: updatedUser._id,
      name: updatedUser.name,
      email: updatedUser.email,
    });
  } else {
    return next(new NotFoundError('User not found'));
  }
});

export {
  authUser,
  registerUser,
  logoutUser,
  getUserProfile,
  updateUserProfile,
};
