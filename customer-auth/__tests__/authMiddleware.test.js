import { jest, describe, it, expect, beforeAll, afterAll, afterEach, beforeEach } from '@jest/globals';
import mongoose from 'mongoose';
import jwt from 'jsonwebtoken';
import { MongoMemoryServer } from 'mongodb-memory-server';
import User from '../models/userModel.js';
import { protect } from '../middleware/authMiddleware.js';

const mockRequest = (headers = {}) => ({
  headers
});

const mockResponse = () => {
  const res = {};
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  return res;
};

let mockNext;

describe('Auth Middleware', () => {
  let mongoServer;
  let testUser;
  const JWT_SECRET = 'test-jwt-secret';

  beforeAll(async () => {
    process.env.JWT_SECRET = JWT_SECRET;
    mongoServer = await MongoMemoryServer.create();
    const mongoUri = mongoServer.getUri();
    await mongoose.connect(mongoUri);
  });

  afterAll(async () => {
    await mongoose.disconnect();
    await mongoServer.stop();
  });

  beforeEach(async () => {
    mockNext = jest.fn();
    await User.deleteMany({});
    
    testUser = await User.create({
      name: 'John Doe',
      email: 'john@example.com',
      password: 'password123'
    });
  });

  describe('protect middleware', () => {
    it('should call next() with valid token', async () => {
      const token = jwt.sign({ userId: testUser._id }, JWT_SECRET);
      const req = mockRequest({ authorization: token });
      const res = mockResponse();

      await protect(req, res, mockNext);

      expect(mockNext).toHaveBeenCalled();
      expect(req.user).toBeDefined();
      expect(req.user.email).toBe('john@example.com');
    });

    it('should set 401 status if no token provided', async () => {
      const req = mockRequest({});
      const res = mockResponse();

      await protect(req, res, mockNext);
      
      expect(res.status).toHaveBeenCalledWith(401);
      expect(mockNext).toHaveBeenCalledWith(expect.any(Error));
      expect(mockNext.mock.calls[0][0].message).toBe('Not authorized, no token');
    });

    it('should set 401 status for invalid token', async () => {
      const req = mockRequest({ authorization: 'invalid-token' });
      const res = mockResponse();

      await protect(req, res, mockNext);
      
      expect(res.status).toHaveBeenCalledWith(401);
      expect(mockNext).toHaveBeenCalledWith(expect.any(Error));
      expect(mockNext.mock.calls[0][0].message).toBe('Not authorized, token failed');
    });

    it('should set 401 status for expired token', async () => {
      const token = jwt.sign({ userId: testUser._id }, JWT_SECRET, { expiresIn: '-1h' });
      const req = mockRequest({ authorization: token });
      const res = mockResponse();

      await protect(req, res, mockNext);
      
      expect(res.status).toHaveBeenCalledWith(401);
      expect(mockNext).toHaveBeenCalledWith(expect.any(Error));
      expect(mockNext.mock.calls[0][0].message).toBe('Not authorized, token failed');
    });

    it('should return 401 for token with non-existent user', async () => {
      const fakeUserId = new mongoose.Types.ObjectId();
      const token = jwt.sign({ userId: fakeUserId }, JWT_SECRET);
      const req = mockRequest({ authorization: token });
      const res = mockResponse();

      await protect(req, res, mockNext);

      expect(mockNext).toHaveBeenCalled();
      expect(req.user).toBeNull();
    });

    it('should not include password in req.user', async () => {
      const token = jwt.sign({ userId: testUser._id }, JWT_SECRET);
      const req = mockRequest({ authorization: token });
      const res = mockResponse();

      await protect(req, res, mockNext);

      expect(req.user.password).toBeUndefined();
    });
  });
});
