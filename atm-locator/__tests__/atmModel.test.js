import { jest, describe, it, expect, beforeAll, afterAll, afterEach, beforeEach } from '@jest/globals';
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import ATM from '../models/atmModel.js';

describe('ATM Model', () => {
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
    await ATM.deleteMany({});
  });

  const validATMData = {
    name: 'Mars Central Bank ATM',
    address: {
      street: '123 Mars Street',
      city: 'Olympus Mons',
      state: 'Mars',
      zip: '00001'
    },
    coordinates: {
      latitude: 18.65,
      longitude: -133.8
    },
    timings: {
      monFri: '9:00 AM - 5:00 PM',
      satSun: '10:00 AM - 2:00 PM',
      holidays: 'Closed'
    },
    atmHours: '24/7',
    numberOfATMs: 3,
    isOpen: true,
    interPlanetary: true
  };

  describe('ATM Schema Validation', () => {
    it('should create an ATM with valid fields', async () => {
      const atm = await ATM.create(validATMData);

      expect(atm.name).toBe(validATMData.name);
      expect(atm.address.street).toBe(validATMData.address.street);
      expect(atm.address.city).toBe(validATMData.address.city);
      expect(atm.coordinates.latitude).toBe(validATMData.coordinates.latitude);
      expect(atm.coordinates.longitude).toBe(validATMData.coordinates.longitude);
      expect(atm.timings.monFri).toBe(validATMData.timings.monFri);
      expect(atm.atmHours).toBe(validATMData.atmHours);
      expect(atm.numberOfATMs).toBe(validATMData.numberOfATMs);
      expect(atm.isOpen).toBe(true);
      expect(atm.interPlanetary).toBe(true);
      expect(atm._id).toBeDefined();
      expect(atm.createdAt).toBeDefined();
      expect(atm.updatedAt).toBeDefined();
    });

    it('should require name field', async () => {
      const atmData = { ...validATMData };
      delete atmData.name;

      await expect(ATM.create(atmData)).rejects.toThrow();
    });

    it('should require address.street field', async () => {
      const atmData = { ...validATMData, address: { ...validATMData.address } };
      delete atmData.address.street;

      await expect(ATM.create(atmData)).rejects.toThrow();
    });

    it('should require address.city field', async () => {
      const atmData = { ...validATMData, address: { ...validATMData.address } };
      delete atmData.address.city;

      await expect(ATM.create(atmData)).rejects.toThrow();
    });

    it('should require address.state field', async () => {
      const atmData = { ...validATMData, address: { ...validATMData.address } };
      delete atmData.address.state;

      await expect(ATM.create(atmData)).rejects.toThrow();
    });

    it('should require address.zip field', async () => {
      const atmData = { ...validATMData, address: { ...validATMData.address } };
      delete atmData.address.zip;

      await expect(ATM.create(atmData)).rejects.toThrow();
    });

    it('should require coordinates.latitude field', async () => {
      const atmData = { ...validATMData, coordinates: { ...validATMData.coordinates } };
      delete atmData.coordinates.latitude;

      await expect(ATM.create(atmData)).rejects.toThrow();
    });

    it('should require coordinates.longitude field', async () => {
      const atmData = { ...validATMData, coordinates: { ...validATMData.coordinates } };
      delete atmData.coordinates.longitude;

      await expect(ATM.create(atmData)).rejects.toThrow();
    });

    it('should require timings.monFri field', async () => {
      const atmData = { ...validATMData, timings: { ...validATMData.timings } };
      delete atmData.timings.monFri;

      await expect(ATM.create(atmData)).rejects.toThrow();
    });

    it('should require timings.satSun field', async () => {
      const atmData = { ...validATMData, timings: { ...validATMData.timings } };
      delete atmData.timings.satSun;

      await expect(ATM.create(atmData)).rejects.toThrow();
    });

    it('should not require timings.holidays field', async () => {
      const atmData = { ...validATMData, timings: { ...validATMData.timings } };
      delete atmData.timings.holidays;

      const atm = await ATM.create(atmData);
      expect(atm.timings.holidays).toBeUndefined();
    });

    it('should require atmHours field', async () => {
      const atmData = { ...validATMData };
      delete atmData.atmHours;

      await expect(ATM.create(atmData)).rejects.toThrow();
    });

    it('should require numberOfATMs field', async () => {
      const atmData = { ...validATMData };
      delete atmData.numberOfATMs;

      await expect(ATM.create(atmData)).rejects.toThrow();
    });

    it('should require isOpen field', async () => {
      const atmData = { ...validATMData };
      delete atmData.isOpen;

      await expect(ATM.create(atmData)).rejects.toThrow();
    });

    it('should default interPlanetary to false', async () => {
      const atmData = { ...validATMData };
      delete atmData.interPlanetary;

      const atm = await ATM.create(atmData);
      expect(atm.interPlanetary).toBe(false);
    });
  });

  describe('ATM Queries', () => {
    beforeEach(async () => {
      await ATM.create([
        { ...validATMData, name: 'ATM 1', isOpen: true, interPlanetary: false },
        { ...validATMData, name: 'ATM 2', isOpen: false, interPlanetary: false },
        { ...validATMData, name: 'ATM 3', isOpen: true, interPlanetary: true },
        { ...validATMData, name: 'ATM 4', isOpen: false, interPlanetary: true }
      ]);
    });

    it('should find all ATMs', async () => {
      const atms = await ATM.find({});
      expect(atms.length).toBe(4);
    });

    it('should find open ATMs', async () => {
      const atms = await ATM.find({ isOpen: true });
      expect(atms.length).toBe(2);
    });

    it('should find interPlanetary ATMs', async () => {
      const atms = await ATM.find({ interPlanetary: true });
      expect(atms.length).toBe(2);
    });

    it('should find open interPlanetary ATMs', async () => {
      const atms = await ATM.find({ isOpen: true, interPlanetary: true });
      expect(atms.length).toBe(1);
      expect(atms[0].name).toBe('ATM 3');
    });

    it('should find ATM by ID', async () => {
      const createdATM = await ATM.create(validATMData);
      const foundATM = await ATM.findById(createdATM._id);

      expect(foundATM).toBeTruthy();
      expect(foundATM.name).toBe(validATMData.name);
    });
  });
});
