import { jest, describe, it, expect, beforeAll, afterAll, afterEach } from '@jest/globals';
import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';
import { MongoMemoryServer } from 'mongodb-memory-server';
import User from '../models/userModel.js';

describe('User Model', () => {
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

  describe('User Schema Validation', () => {
    it('should create a user with valid fields', async () => {
      const userData = {
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      };

      const user = await User.create(userData);

      expect(user.name).toBe(userData.name);
      expect(user.email).toBe(userData.email);
      expect(user.password).not.toBe(userData.password);
      expect(user._id).toBeDefined();
      expect(user.createdAt).toBeDefined();
      expect(user.updatedAt).toBeDefined();
    });

    it('should require name field', async () => {
      const userData = {
        email: 'john@example.com',
        password: 'password123'
      };

      await expect(User.create(userData)).rejects.toThrow();
    });

    it('should require email field', async () => {
      const userData = {
        name: 'John Doe',
        password: 'password123'
      };

      await expect(User.create(userData)).rejects.toThrow();
    });

    it('should require password field', async () => {
      const userData = {
        name: 'John Doe',
        email: 'john@example.com'
      };

      await expect(User.create(userData)).rejects.toThrow();
    });

    it('should enforce unique email constraint', async () => {
      const userData = {
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      };

      await User.create(userData);

      const duplicateUser = {
        name: 'Jane Doe',
        email: 'john@example.com',
        password: 'password456'
      };

      await expect(User.create(duplicateUser)).rejects.toThrow();
    });
  });

  describe('Password Hashing', () => {
    it('should hash password before saving', async () => {
      const plainPassword = 'password123';
      const user = await User.create({
        name: 'John Doe',
        email: 'john@example.com',
        password: plainPassword
      });

      expect(user.password).not.toBe(plainPassword);
      const isMatch = await bcrypt.compare(plainPassword, user.password);
      expect(isMatch).toBe(true);
    });

    it('should not rehash password if not modified', async () => {
      const user = await User.create({
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      });

      const originalHash = user.password;
      user.name = 'John Updated';
      await user.save();

      expect(user.password).toBe(originalHash);
    });

    it('should rehash password when password is modified', async () => {
      const user = await User.create({
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      });

      const originalHash = user.password;
      user.password = 'newpassword456';
      await user.save();

      expect(user.password).not.toBe(originalHash);
      expect(user.password).not.toBe('newpassword456');
    });
  });

  describe('matchPassword Method', () => {
    it('should return true for correct password', async () => {
      const plainPassword = 'password123';
      const user = await User.create({
        name: 'John Doe',
        email: 'john@example.com',
        password: plainPassword
      });

      const isMatch = await user.matchPassword(plainPassword);
      expect(isMatch).toBe(true);
    });

    it('should return false for incorrect password', async () => {
      const user = await User.create({
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      });

      const isMatch = await user.matchPassword('wrongpassword');
      expect(isMatch).toBe(false);
    });

    it('should return false for empty password', async () => {
      const user = await User.create({
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      });

      const isMatch = await user.matchPassword('');
      expect(isMatch).toBe(false);
    });
  });
});
