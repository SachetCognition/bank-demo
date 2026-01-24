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
  getUserProfile,
  updateUserProfile,
} from '../controllers/userController.js';
import { protect } from '../middleware/authMiddleware.js';
import { validateRequest, sanitizeQueryParams } from '../middleware/validateRequest.js';
import {
  registerUserSchema,
  authUserSchema,
  getUserProfileSchema,
  updateUserProfileSchema,
} from '../middleware/validationSchemas.js';

const router = express.Router();

router.use(sanitizeQueryParams);

router.post('/', validateRequest(registerUserSchema), registerUser);

router.post('/auth', validateRequest(authUserSchema), authUser);

router.post('/logout', logoutUser);

router.route('/profile')
  .post(validateRequest(getUserProfileSchema), getUserProfile)
  .put(validateRequest(updateUserProfileSchema), updateUserProfile);

// router
//   .route("/profile")
//   .get(protect, getUserProfile)
//   .put(protect, updateUserProfile);

export default router;
