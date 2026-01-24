/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import asyncHandler from "express-async-handler";
import ATM from "../models/atmModel.js";
import logger from "../utils/logger.js";
import { NotFoundError, ValidationError, InternalError } from "../utils/errors.js";

// @desc    Returns list of all ATMs
// @route   POST /api/atm
// @access  Public
const getATMs = asyncHandler(async (req, res, next) => {
  const reqLogger = req.logger || logger;
  
  let query = {
    interPlanetary: false,
  };
  if (req.body.isOpenNow) {
    query.isOpen = true;
  }
  if (req.body.isInterPlanetary) {
    query.interPlanetary = true;
  }
  
  const ATMs = await ATM.find(query, {
    name: 1,
    coordinates: 1,
    address: 1,
    isOpen: 1,
  });
  
  const shuffledATMs = [...ATMs].sort(() => Math.random() - 0.5).slice(0, 4);
  
  if (shuffledATMs && shuffledATMs.length > 0) {
    reqLogger.info('ATMs retrieved successfully', { count: shuffledATMs.length, query });
    res.status(200).json(shuffledATMs);
  } else {
    return next(new NotFoundError("No ATMs found"));
  }
});

// @desc    Add new ATM
// @route   POST /atm/add
// @access  Private
const addATM = asyncHandler(async (req, res, next) => {
  const reqLogger = req.logger || logger;
  
  const {
    name,
    street,
    city,
    state,
    zip,
    latitude,
    longitude,
    monFri,
    satSun,
    holidays,
    atmHours,
    numberOfATMs,
    isOpen,
    interPlanetary,
  } = req.body;

  if (!name) {
    return next(new ValidationError("ATM name is required"));
  }

  const atm = new ATM({
    name,
    address: {
      street,
      city,
      state,
      zip,
    },
    coordinates: {
      latitude,
      longitude,
    },
    timings: {
      monFri,
      satSun,
      holidays,
    },
    atmHours,
    numberOfATMs,
    isOpen,
    interPlanetary,
  });

  const createdATM = await atm.save();
  if (createdATM) {
    reqLogger.info('ATM created successfully', { atmId: createdATM._id, name: createdATM.name });
    res.status(201).json(createdATM);
  } else {
    return next(new InternalError("Could not create ATM"));
  }
});

// @desc    Add specific ATM data
// @route   GET /atm/:id
// @access  Public
const getSpecificATM = asyncHandler(async (req, res, next) => {
  const reqLogger = req.logger || logger;
  
  const atm = await ATM.findById(req.params.id);
  if (atm) {
    reqLogger.info('ATM details retrieved', { atmId: req.params.id });
    res.status(200).json({
      coordinates: atm.coordinates,
      timings: atm.timings,
      atmHours: atm.atmHours,
      numberOfATMs: atm.numberOfATMs,
      isOpen: atm.isOpen,
    });
  } else {
    return next(new NotFoundError("ATM information not found"));
  }
});

export { getATMs, addATM, getSpecificATM };
