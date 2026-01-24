/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import Joi from "joi";

export const getATMsSchema = Joi.object({
  isOpenNow: Joi.boolean()
    .optional()
    .messages({
      "boolean.base": "isOpenNow must be a boolean value",
    }),
  isInterPlanetary: Joi.boolean()
    .optional()
    .messages({
      "boolean.base": "isInterPlanetary must be a boolean value",
    }),
});

export const addATMSchema = Joi.object({
  name: Joi.string()
    .min(2)
    .max(200)
    .trim()
    .required()
    .messages({
      "string.min": "ATM name must be at least 2 characters long",
      "string.max": "ATM name must not exceed 200 characters",
      "any.required": "ATM name is required",
    }),
  street: Joi.string()
    .min(2)
    .max(300)
    .trim()
    .required()
    .messages({
      "string.min": "Street must be at least 2 characters long",
      "string.max": "Street must not exceed 300 characters",
      "any.required": "Street is required",
    }),
  city: Joi.string()
    .min(2)
    .max(100)
    .trim()
    .required()
    .messages({
      "string.min": "City must be at least 2 characters long",
      "string.max": "City must not exceed 100 characters",
      "any.required": "City is required",
    }),
  state: Joi.string()
    .min(2)
    .max(100)
    .trim()
    .required()
    .messages({
      "string.min": "State must be at least 2 characters long",
      "string.max": "State must not exceed 100 characters",
      "any.required": "State is required",
    }),
  zip: Joi.string()
    .pattern(/^[0-9A-Za-z\-\s]{3,20}$/)
    .trim()
    .required()
    .messages({
      "string.pattern.base": "Please provide a valid zip code",
      "any.required": "Zip code is required",
    }),
  latitude: Joi.number()
    .min(-90)
    .max(90)
    .required()
    .messages({
      "number.min": "Latitude must be between -90 and 90",
      "number.max": "Latitude must be between -90 and 90",
      "any.required": "Latitude is required",
    }),
  longitude: Joi.number()
    .min(-180)
    .max(180)
    .required()
    .messages({
      "number.min": "Longitude must be between -180 and 180",
      "number.max": "Longitude must be between -180 and 180",
      "any.required": "Longitude is required",
    }),
  monFri: Joi.string()
    .max(100)
    .trim()
    .optional()
    .messages({
      "string.max": "Monday-Friday hours must not exceed 100 characters",
    }),
  satSun: Joi.string()
    .max(100)
    .trim()
    .optional()
    .messages({
      "string.max": "Saturday-Sunday hours must not exceed 100 characters",
    }),
  holidays: Joi.string()
    .max(100)
    .trim()
    .optional()
    .messages({
      "string.max": "Holiday hours must not exceed 100 characters",
    }),
  atmHours: Joi.string()
    .max(100)
    .trim()
    .optional()
    .messages({
      "string.max": "ATM hours must not exceed 100 characters",
    }),
  numberOfATMs: Joi.number()
    .integer()
    .min(1)
    .max(100)
    .optional()
    .messages({
      "number.min": "Number of ATMs must be at least 1",
      "number.max": "Number of ATMs must not exceed 100",
      "number.integer": "Number of ATMs must be a whole number",
    }),
  isOpen: Joi.boolean()
    .optional()
    .messages({
      "boolean.base": "isOpen must be a boolean value",
    }),
  interPlanetary: Joi.boolean()
    .optional()
    .messages({
      "boolean.base": "interPlanetary must be a boolean value",
    }),
});

export const getSpecificATMSchema = Joi.object({
  id: Joi.string()
    .pattern(/^[0-9a-fA-F]{24}$/)
    .required()
    .messages({
      "string.pattern.base": "Please provide a valid ATM ID",
      "any.required": "ATM ID is required",
    }),
});
