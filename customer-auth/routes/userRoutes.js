/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import express from "express";
import {
  authUser,
  registerUser,
  logoutUser,
  getUserProfile,
  updateUserProfile,
} from "../controllers/userController.js";
import { protect } from "../middleware/authMiddleware.js";
import { registerValidation, loginValidation } from "../middleware/validationMiddleware.js";
import { generateCsrfToken, validateCsrf } from "../middleware/csrfMiddleware.js";

const router = express.Router();

router.get("/csrf-token", generateCsrfToken);

router.post("/", registerValidation, validateCsrf, registerUser);

router.post("/auth", loginValidation, validateCsrf, authUser);

router.post("/logout", logoutUser);

router
  .route("/profile")
  .get(protect, getUserProfile)
  .put(protect, validateCsrf, updateUserProfile);

export default router;
