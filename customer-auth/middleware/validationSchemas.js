/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import Joi from 'joi';

const passwordPattern = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;

export const registerUserSchema = Joi.object({
  name: Joi.string()
    .min(2)
    .max(100)
    .trim()
    .required()
    .messages({
      'string.min': 'Name must be at least 2 characters long',
      'string.max': 'Name must not exceed 100 characters',
      'any.required': 'Name is required',
    }),
  email: Joi.string()
    .email()
    .max(255)
    .lowercase()
    .trim()
    .required()
    .messages({
      'string.email': 'Please provide a valid email address',
      'string.max': 'Email must not exceed 255 characters',
      'any.required': 'Email is required',
    }),
  password: Joi.string()
    .min(8)
    .max(128)
    .pattern(passwordPattern)
    .required()
    .messages({
      'string.min': 'Password must be at least 8 characters long',
      'string.max': 'Password must not exceed 128 characters',
      'string.pattern.base': 'Password must contain at least one letter, one digit, and one special character (@$!%*#?&)',
      'any.required': 'Password is required',
    }),
});

export const authUserSchema = Joi.object({
  email: Joi.string()
    .email()
    .max(255)
    .lowercase()
    .trim()
    .required()
    .messages({
      'string.email': 'Please provide a valid email address',
      'string.max': 'Email must not exceed 255 characters',
      'any.required': 'Email is required',
    }),
  password: Joi.string()
    .min(1)
    .max(128)
    .required()
    .messages({
      'string.min': 'Password is required',
      'string.max': 'Password must not exceed 128 characters',
      'any.required': 'Password is required',
    }),
});

export const getUserProfileSchema = Joi.object({
  email: Joi.string()
    .email()
    .max(255)
    .lowercase()
    .trim()
    .required()
    .messages({
      'string.email': 'Please provide a valid email address',
      'string.max': 'Email must not exceed 255 characters',
      'any.required': 'Email is required',
    }),
});

export const updateUserProfileSchema = Joi.object({
  email: Joi.string()
    .email()
    .max(255)
    .lowercase()
    .trim()
    .required()
    .messages({
      'string.email': 'Please provide a valid email address',
      'string.max': 'Email must not exceed 255 characters',
      'any.required': 'Email is required',
    }),
  password: Joi.string()
    .min(8)
    .max(128)
    .pattern(passwordPattern)
    .optional()
    .messages({
      'string.min': 'Password must be at least 8 characters long',
      'string.max': 'Password must not exceed 128 characters',
      'string.pattern.base': 'Password must contain at least one letter, one digit, and one special character (@$!%*#?&)',
    }),
});
