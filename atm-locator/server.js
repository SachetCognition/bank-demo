/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import path from "path";
import express from "express";
import dotenv from "dotenv";

import cors from "cors";
import cookieParser from "cookie-parser";

import { swaggerDocs } from './utils/swagger.js';

import { notFound, errorHandler } from "./middleware/errorMiddleware.js";
import { requestLogger } from "./middleware/requestLogger.js";

import atmRoutes from "./routes/atmRoutes.js";
import healthRoutes from "./routes/healthRoutes.js";

import logger from "./utils/logger.js";

// Load environment variables from .env file
dotenv.config();

// connect to MongoDB Atlas database
import connectDB from "./config/db.js";
connectDB();

const port = process.env.PORT || 8001;
const app = express();

// mounting middlewares
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cors({credentials: true, origin: true}));
app.use(cookieParser());
app.use(requestLogger);

// mounting routes
app.use("/api/atm", atmRoutes);
app.use("/", healthRoutes);

// Swagger documentation
swaggerDocs(app, port);

// error handling middlewares
app.use(notFound);
app.use(errorHandler);

app.listen(port, () =>
  logger.info(`atm-locator server started on port ${port}`, { port })
);
