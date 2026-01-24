/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import express from 'express';
import {
  authUser,
  registerUser,
  logoutUser,
  refreshToken,
  getUserProfile,
  updateUserProfile,
} from '../controllers/userController.js';
import { protect, authorize } from '../middleware/authMiddleware.js';

const router = express.Router();

// Public routes
router.post('/', registerUser);
router.post('/auth', authUser);
router.post('/logout', logoutUser);
router.post('/refresh', refreshToken);

// Protected routes - require authentication
router
  .route('/profile')
  .get(protect, getUserProfile)
  .post(protect, getUserProfile)
  .put(protect, updateUserProfile);

// Admin-only routes (example)
router.get('/admin/users', protect, authorize('admin'), (req, res) => {
  res.json({ message: 'Admin access granted' });
});

export default router;
