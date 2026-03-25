/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import asyncHandler from "express-async-handler";
import User from "../models/userModel.js";
import logAudit from "../utils/auditLogger.js";
import generateToken from "../utils/generateToken.js";
// import { Worker } from 'worker_threads';

// @desc    Register a new user
// @route   POST /api/users
// @access  Public
const registerUser = asyncHandler(async (req, res) => {
  try {
    const { name, email, password } = req.body;

    if (!name || !email || !password) {
      res.status(400);
      throw new Error("Name, email and password are required");
    }

    const userExists = await User.findOne({ email });

    if (userExists) {
      res.status(400);
      throw new Error("User already exists");
    }

    const user = await User.create({
      name,
      email,
      password,
    });

    if (user) {
      generateToken(res, user._id);
      await logAudit('registration', email, { name }, req.ip);
      res.status(200).json({
        _id: user._id,
        name: user.name,
        email: user.email,
      });
    } else {
      res.status(400);
      throw new Error("Invalid user data");
    }
  } catch (error) {
    res.status(res.statusCode === 200 ? 500 : res.statusCode);
    res.json({
      message: error.message || "Internal Server Error",
      stack: process.env.NODE_ENV === "production" ? null : error.stack,
    });
  }
});

// @desc    Auth user & get token
// @route   POST /api/users/auth
// @access  Public
const authUser = asyncHandler(async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      res.status(400);
      throw new Error("Email and password are required");
    }

    const user = await User.findOne({ email });

    if (user && (await user.matchPassword(password))) {
      if (user.twoFactorEnabled) {
        const { totpCode } = req.body;
        if (!totpCode) {
          return res.status(200).json({
            requires2FA: true,
            message: "2FA code required",
          });
        }
        const { authenticator } = await import('otplib');
        const isValid = authenticator.verify({ token: totpCode, secret: user.twoFactorSecret });
        if (!isValid) {
          res.status(400);
          throw new Error("Invalid 2FA code");
        }
      }
      generateToken(res, user._id);
      await logAudit('login_success', email, {}, req.ip);
      res.json({
        _id: user._id,
        name: user.name,
        email: user.email,
      });
    } else {
      await logAudit('login_failure', email, { reason: 'Invalid credentials' }, req.ip);
      res.status(400);
      throw new Error("Invalid email or password");
    }
  } catch (error) {
    res.status(res.statusCode === 200 ? 500 : res.statusCode);
    res.json({
      status: false,
      message: error.message || "Internal Server Error",
      stack: process.env.NODE_ENV === "production" ? null : error.stack,
    });
  }

  // const worker = new Worker('./workers/authWorker.js');

  // worker.on('message', (result) => {
  //   if (result.valid) {
  //     generateToken(res, result.user._id);
  //     res.json({
  //       _id: result.user._id,
  //       name: result.user.name,
  //       email: result.user.email,
  //     });
  //   } else {
  //     res.status(401);
  //     throw new Error('Invalid email or password');
  //   }
  // });
  // worker.postMessage({ email, password });
});

// @desc    Logout user and clear cookie
// @route   POST /api/users/logout
// @access  Public
const logoutUser = (req, res) => {
  try {
    res.cookie("jwt", "", {
      httpOnly: true,
      expires: new Date(0),
    });
    res.status(200).json({ message: "Logged out successfully" });
  } catch (error) {
    res.status(res.statusCode === 200 ? 500 : res.statusCode);
    res.json({
      message: error.message || "Internal Server Error",
      stack: process.env.NODE_ENV === "production" ? null : error.stack,
    });
  }
};

// @desc    Get user profile
// @route   GET api/users/profile
// @access  Private
const getUserProfile = asyncHandler(async (req, res) => {
  try {
    const user = req.user;

    if (user) {
      res.json({
        _id: user._id,
        name: user.name,
        email: user.email,
      });
    } else {
      res.status(404);
      throw new Error("User not found");
    }
  } catch (error) {
    res.status(res.statusCode === 200 ? 500 : res.statusCode);
    res.json({
      message: error.message || "Internal Server Error",
      stack: process.env.NODE_ENV === "production" ? null : error.stack,
      feedback: "",
    });
  }
});

// @desc    Update user profile
// @route   PUT /api/users/profile
// @access  Private
const updateUserProfile = asyncHandler(async (req, res) => {
  try {
    const user = await User.findOne({email: req.body.email});

    if (user) {
      user.password = req.body.password || user.password;

      const updatedUser = await user.save();

      await logAudit('profile_update', req.body.email, {}, req.ip);
      res.json({
        _id: updatedUser._id,
        name: updatedUser.name,
        email: updatedUser.email,
      });
      
    } else {
      res.status(404);
      throw new Error("User not found");
    }
  } catch (error) {
    res.status(res.statusCode === 200 ? 500 : res.statusCode);
    res.json({
      message: error.message || "Internal Server Error",
      stack: process.env.NODE_ENV === "production" ? null : error.stack,
      feedback: "",
    });
  }
});

// POST /api/users/2fa/setup - Generate TOTP secret
const setup2FA = asyncHandler(async (req, res) => {
  try {
    const user = req.user;
    if (!user) {
      res.status(401);
      throw new Error("Not authorized");
    }
    
    const { authenticator } = await import('otplib');
    const secret = authenticator.generateSecret();
    
    user.twoFactorSecret = secret;
    await user.save();
    
    const otpauth = authenticator.keyuri(user.email, 'MartianBank', secret);
    
    res.json({
      secret,
      otpauth_url: otpauth,
      message: "Scan the QR code with your authenticator app, then verify with /api/users/2fa/verify",
    });
  } catch (error) {
    res.status(500);
    res.json({ message: error.message });
  }
});

// POST /api/users/2fa/verify - Verify TOTP and enable 2FA
const verify2FA = asyncHandler(async (req, res) => {
  try {
    const user = req.user;
    const { token } = req.body;
    
    if (!user || !user.twoFactorSecret) {
      res.status(400);
      throw new Error("2FA not set up. Call /api/users/2fa/setup first");
    }
    
    const { authenticator } = await import('otplib');
    const isValid = authenticator.verify({ token, secret: user.twoFactorSecret });
    
    if (isValid) {
      user.twoFactorEnabled = true;
      await user.save();
      res.json({ message: "2FA enabled successfully" });
    } else {
      res.status(400);
      throw new Error("Invalid TOTP code");
    }
  } catch (error) {
    res.status(res.statusCode === 200 ? 500 : res.statusCode);
    res.json({ message: error.message });
  }
});

const dataErasure = asyncHandler(async (req, res) => {
  try {
    const user = req.user; // from protect middleware
    if (!user) {
      res.status(401);
      throw new Error("Not authorized");
    }
    
    // Anonymize user data
    user.name = "[REDACTED]";
    user.email = `redacted_${user._id}@redacted.com`;
    await user.save();

    // Clear JWT cookie
    res.cookie("jwt", "", { httpOnly: true, expires: new Date(0) });
    
    await logAudit('data_erasure', 'redacted', { userId: user._id.toString() }, req.ip);
    
    res.status(200).json({ message: "Your personal data has been anonymized. Financial records are retained per regulatory requirements." });
  } catch (error) {
    res.status(res.statusCode === 200 ? 500 : res.statusCode);
    res.json({ message: error.message || "Internal Server Error" });
  }
});

const dataExport = asyncHandler(async (req, res) => {
  try {
    const user = req.user;
    if (!user) {
      res.status(401);
      throw new Error("Not authorized");
    }

    const userData = {
      profile: { name: user.name, email: user.email, createdAt: user.createdAt },
      // Note: In a full implementation, you'd query accounts, transactions, loans services
      // For now, export the user profile data
      exportDate: new Date().toISOString(),
      format: "GDPR Data Export",
    };

    await logAudit('data_export', user.email, {}, req.ip);
    
    res.setHeader('Content-Disposition', 'attachment; filename=user-data-export.json');
    res.setHeader('Content-Type', 'application/json');
    res.status(200).json(userData);
  } catch (error) {
    res.status(res.statusCode === 200 ? 500 : res.statusCode);
    res.json({ message: error.message || "Internal Server Error" });
  }
});

export {
  authUser,
  registerUser,
  logoutUser,
  getUserProfile,
  updateUserProfile,
  setup2FA,
  verify2FA,
  dataErasure,
  dataExport,
};
