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
  checkAuth,
  getUserProfile,
  updateUserProfile,
} from '../controllers/userController.js';
import { protect } from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/', registerUser);

router.post('/auth', authUser);

router.post('/logout', logoutUser);

router.get('/check-auth', protect, checkAuth);

router.route('/profile').post(getUserProfile).put(updateUserProfile);

export default router;
