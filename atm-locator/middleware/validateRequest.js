/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import mongoSanitize from "mongo-sanitize";

const sanitizeInput = (obj) => {
  if (obj === null || obj === undefined) {
    return obj;
  }

  if (typeof obj === "string") {
    return mongoSanitize(obj);
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => sanitizeInput(item));
  }

  if (typeof obj === "object") {
    const sanitized = {};
    Object.keys(obj).forEach((key) => {
      const sanitizedKey = mongoSanitize(key);
      if (typeof sanitizedKey === "string" && !sanitizedKey.startsWith("$")) {
        sanitized[sanitizedKey] = sanitizeInput(obj[key]);
      }
    });
    return sanitized;
  }

  return obj;
};

const validateRequest = (schema) => (req, res, next) => {
  const sanitizedBody = sanitizeInput(req.body);
  req.body = sanitizedBody;

  const { error, value } = schema.validate(sanitizedBody, {
    abortEarly: false,
    stripUnknown: true,
  });

  if (error) {
    const errorMessages = error.details.map((detail) => detail.message);
    return res.status(400).json({
      success: false,
      message: "Validation failed",
      errors: errorMessages,
    });
  }

  req.body = value;
  return next();
};

const validateParams = (schema) => (req, res, next) => {
  const sanitizedParams = sanitizeInput(req.params);
  req.params = sanitizedParams;

  const { error, value } = schema.validate(sanitizedParams, {
    abortEarly: false,
    stripUnknown: true,
  });

  if (error) {
    const errorMessages = error.details.map((detail) => detail.message);
    return res.status(400).json({
      success: false,
      message: "Validation failed",
      errors: errorMessages,
    });
  }

  req.params = value;
  return next();
};

const sanitizeQueryParams = (req, res, next) => {
  if (req.query) {
    req.query = sanitizeInput(req.query);
  }
  if (req.params) {
    req.params = sanitizeInput(req.params);
  }
  next();
};

export { validateRequest, validateParams, sanitizeInput, sanitizeQueryParams };
