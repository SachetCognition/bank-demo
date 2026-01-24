import { jest, describe, it, expect, beforeAll, afterAll, afterEach, beforeEach } from '@jest/globals';
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import User from '../models/userModel.js';
import {
  registerUser,
  authUser,
  logoutUser,
  getUserProfile,
  updateUserProfile
} from '../controllers/userController.js';

const mockRequest = (body = {}, params = {}, headers = {}) => ({
  body,
  params,
  headers
});

const mockResponse = () => {
  const res = {};
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  return res;
};

describe('User Controller', () => {
  let mongoServer;

  beforeAll(async () => {
    mongoServer = await MongoMemoryServer.create();
    const mongoUri = mongoServer.getUri();
    await mongoose.connect(mongoUri);
  });

  afterAll(async () => {
    await mongoose.disconnect();
    await mongoServer.stop();
  });

  afterEach(async () => {
    await User.deleteMany({});
  });

  describe('registerUser', () => {
    it('should register a new user successfully', async () => {
      const req = mockRequest({
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      });
      const res = mockResponse();

      await registerUser(req, res);

      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'John Doe',
          email: 'john@example.com'
        })
      );

      const user = await User.findOne({ email: 'john@example.com' });
      expect(user).toBeTruthy();
      expect(user.name).toBe('John Doe');
    });

    it('should return 400 if name is missing', async () => {
      const req = mockRequest({
        email: 'john@example.com',
        password: 'password123'
      });
      const res = mockResponse();

      await registerUser(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Name, email and password are required'
        })
      );
    });

    it('should return 400 if email is missing', async () => {
      const req = mockRequest({
        name: 'John Doe',
        password: 'password123'
      });
      const res = mockResponse();

      await registerUser(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Name, email and password are required'
        })
      );
    });

    it('should return 400 if password is missing', async () => {
      const req = mockRequest({
        name: 'John Doe',
        email: 'john@example.com'
      });
      const res = mockResponse();

      await registerUser(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Name, email and password are required'
        })
      );
    });

    it('should return 400 if user already exists', async () => {
      await User.create({
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      });

      const req = mockRequest({
        name: 'Jane Doe',
        email: 'john@example.com',
        password: 'password456'
      });
      const res = mockResponse();

      await registerUser(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'User already exists'
        })
      );
    });
  });

  describe('authUser', () => {
    beforeEach(async () => {
      await User.create({
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      });
    });

    it('should authenticate user with valid credentials', async () => {
      const req = mockRequest({
        email: 'john@example.com',
        password: 'password123'
      });
      const res = mockResponse();

      await authUser(req, res);

      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'John Doe',
          email: 'john@example.com'
        })
      );
    });

    it('should return 400 if email is missing', async () => {
      const req = mockRequest({
        password: 'password123'
      });
      const res = mockResponse();

      await authUser(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Email and password are required'
        })
      );
    });

    it('should return 400 if password is missing', async () => {
      const req = mockRequest({
        email: 'john@example.com'
      });
      const res = mockResponse();

      await authUser(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Email and password are required'
        })
      );
    });

    it('should return 400 for invalid email', async () => {
      const req = mockRequest({
        email: 'wrong@example.com',
        password: 'password123'
      });
      const res = mockResponse();

      await authUser(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Invalid email or password'
        })
      );
    });

    it('should return 400 for invalid password', async () => {
      const req = mockRequest({
        email: 'john@example.com',
        password: 'wrongpassword'
      });
      const res = mockResponse();

      await authUser(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Invalid email or password'
        })
      );
    });
  });

  describe('logoutUser', () => {
    it('should logout user successfully', () => {
      const req = mockRequest();
      const res = mockResponse();

      logoutUser(req, res);

      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith({
        message: 'Logged out successfully'
      });
    });
  });

  describe('getUserProfile', () => {
    beforeEach(async () => {
      await User.create({
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      });
    });

    it('should return user profile for valid email', async () => {
      const req = mockRequest({
        email: 'john@example.com'
      });
      const res = mockResponse();

      await getUserProfile(req, res);

      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'John Doe',
          email: 'john@example.com'
        })
      );
    });

    it('should return 404 for non-existent user', async () => {
      const req = mockRequest({
        email: 'nonexistent@example.com'
      });
      const res = mockResponse();

      await getUserProfile(req, res);

      expect(res.status).toHaveBeenCalledWith(404);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'User not found'
        })
      );
    });
  });

  describe('updateUserProfile', () => {
    beforeEach(async () => {
      await User.create({
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      });
    });

    it('should update user password successfully', async () => {
      const req = mockRequest({
        email: 'john@example.com',
        password: 'newpassword456'
      });
      const res = mockResponse();

      await updateUserProfile(req, res);

      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'John Doe',
          email: 'john@example.com'
        })
      );

      const updatedUser = await User.findOne({ email: 'john@example.com' });
      const isMatch = await updatedUser.matchPassword('newpassword456');
      expect(isMatch).toBe(true);
    });

    it('should return 404 for non-existent user', async () => {
      const req = mockRequest({
        email: 'nonexistent@example.com',
        password: 'newpassword456'
      });
      const res = mockResponse();

      await updateUserProfile(req, res);

      expect(res.status).toHaveBeenCalledWith(404);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'User not found'
        })
      );
    });
  });
});
