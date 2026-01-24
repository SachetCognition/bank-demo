/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import express from "express";
import {
  getATMs,
  addATM,
  getSpecificATM,
} from "../controllers/atmController.js";
import { validateRequest, validateParams, sanitizeQueryParams } from "../middleware/validateRequest.js";
import {
  getATMsSchema,
  addATMSchema,
  getSpecificATMSchema,
} from "../middleware/validationSchemas.js";

const router = express.Router();

router.use(sanitizeQueryParams);

router.post("/", validateRequest(getATMsSchema), getATMs);
router.post("/add", validateRequest(addATMSchema), addATM);
router.get("/:id", validateParams(getSpecificATMSchema), getSpecificATM);

export default router;
