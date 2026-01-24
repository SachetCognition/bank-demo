import { jest, describe, it, expect, beforeAll, afterAll, afterEach, beforeEach } from '@jest/globals';
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import ATM from '../models/atmModel.js';
import { getATMs, addATM, getSpecificATM } from '../controllers/atmController.js';

const mockRequest = (body = {}, params = {}) => ({
  body,
  params
});

const mockResponse = () => {
  const res = {};
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  return res;
};

describe('ATM Controller', () => {
  let mongoServer;

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
    interPlanetary: false
  };

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

  describe('getATMs', () => {
    beforeEach(async () => {
      await ATM.create([
        { ...validATMData, name: 'ATM 1', isOpen: true, interPlanetary: false },
        { ...validATMData, name: 'ATM 2', isOpen: false, interPlanetary: false },
        { ...validATMData, name: 'ATM 3', isOpen: true, interPlanetary: true },
        { ...validATMData, name: 'ATM 4', isOpen: false, interPlanetary: true },
        { ...validATMData, name: 'ATM 5', isOpen: true, interPlanetary: false }
      ]);
    });

    it('should return non-interPlanetary ATMs by default', async () => {
      const req = mockRequest({});
      const res = mockResponse();

      await getATMs(req, res);

      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalled();
      const result = res.json.mock.calls[0][0];
      expect(result.length).toBeLessThanOrEqual(4);
      result.forEach(atm => {
        expect(atm.interPlanetary).toBeUndefined();
      });
    });

    it('should filter by isOpenNow when provided', async () => {
      const req = mockRequest({ isOpenNow: true });
      const res = mockResponse();

      await getATMs(req, res);

      expect(res.status).toHaveBeenCalledWith(200);
      const result = res.json.mock.calls[0][0];
      expect(result.length).toBeLessThanOrEqual(4);
    });

    it('should return interPlanetary ATMs when isInterPlanetary is true', async () => {
      const req = mockRequest({ isInterPlanetary: true });
      const res = mockResponse();

      await getATMs(req, res);

      expect(res.status).toHaveBeenCalledWith(200);
      const result = res.json.mock.calls[0][0];
      expect(result.length).toBeLessThanOrEqual(4);
    });

    it('should filter by both isOpenNow and isInterPlanetary', async () => {
      const req = mockRequest({ isOpenNow: true, isInterPlanetary: true });
      const res = mockResponse();

      await getATMs(req, res);

      expect(res.status).toHaveBeenCalledWith(200);
      const result = res.json.mock.calls[0][0];
      expect(result.length).toBeLessThanOrEqual(4);
    });

    it('should return at most 4 ATMs', async () => {
      await ATM.create([
        { ...validATMData, name: 'ATM 6', isOpen: true, interPlanetary: false },
        { ...validATMData, name: 'ATM 7', isOpen: true, interPlanetary: false }
      ]);

      const req = mockRequest({});
      const res = mockResponse();

      await getATMs(req, res);

      expect(res.status).toHaveBeenCalledWith(200);
      const result = res.json.mock.calls[0][0];
      expect(result.length).toBeLessThanOrEqual(4);
    });

    it('should return ATMs with required fields only', async () => {
      const req = mockRequest({});
      const res = mockResponse();

      await getATMs(req, res);

      expect(res.status).toHaveBeenCalledWith(200);
      const result = res.json.mock.calls[0][0];
      result.forEach(atm => {
        expect(atm.name).toBeDefined();
        expect(atm.coordinates).toBeDefined();
        expect(atm.address).toBeDefined();
        expect(atm.isOpen).toBeDefined();
      });
    });
  });

  describe('addATM', () => {
    it('should create a new ATM successfully', async () => {
      const req = mockRequest({
        name: 'New Mars ATM',
        street: '456 Mars Avenue',
        city: 'Valles Marineris',
        state: 'Mars',
        zip: '00002',
        latitude: 14.5,
        longitude: -59.2,
        monFri: '8:00 AM - 6:00 PM',
        satSun: '9:00 AM - 3:00 PM',
        holidays: 'Closed',
        atmHours: '24/7',
        numberOfATMs: 2,
        isOpen: true,
        interPlanetary: true
      });
      const res = mockResponse();

      await addATM(req, res);

      expect(res.status).toHaveBeenCalledWith(201);
      expect(res.json).toHaveBeenCalled();
      const result = res.json.mock.calls[0][0];
      expect(result.name).toBe('New Mars ATM');
      expect(result.address.street).toBe('456 Mars Avenue');
      expect(result.coordinates.latitude).toBe(14.5);
      expect(result.interPlanetary).toBe(true);

      const savedATM = await ATM.findOne({ name: 'New Mars ATM' });
      expect(savedATM).toBeTruthy();
    });

    it('should create ATM with all required fields', async () => {
      const req = mockRequest({
        name: 'Complete ATM',
        street: '789 Mars Blvd',
        city: 'Hellas Basin',
        state: 'Mars',
        zip: '00003',
        latitude: -42.7,
        longitude: 70.0,
        monFri: '7:00 AM - 7:00 PM',
        satSun: '8:00 AM - 4:00 PM',
        holidays: 'Limited Hours',
        atmHours: '6:00 AM - 11:00 PM',
        numberOfATMs: 5,
        isOpen: false,
        interPlanetary: false
      });
      const res = mockResponse();

      await addATM(req, res);

      expect(res.status).toHaveBeenCalledWith(201);
      const result = res.json.mock.calls[0][0];
      expect(result.timings.holidays).toBe('Limited Hours');
      expect(result.numberOfATMs).toBe(5);
      expect(result.isOpen).toBe(false);
    });
  });

  describe('getSpecificATM', () => {
    let testATM;

    beforeEach(async () => {
      testATM = await ATM.create(validATMData);
    });

    it('should return ATM details for valid ID', async () => {
      const req = mockRequest({}, { id: testATM._id.toString() });
      const res = mockResponse();

      await getSpecificATM(req, res);

      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith({
        coordinates: testATM.coordinates,
        timings: testATM.timings,
        atmHours: testATM.atmHours,
        numberOfATMs: testATM.numberOfATMs,
        isOpen: testATM.isOpen
      });
    });

    it('should return 404 for non-existent ATM ID', async () => {
      const fakeId = new mongoose.Types.ObjectId();
      const req = mockRequest({}, { id: fakeId.toString() });
      const res = mockResponse();

      await expect(getSpecificATM(req, res)).rejects.toThrow('ATM not found');
      expect(res.status).toHaveBeenCalledWith(404);
      expect(res.json).toHaveBeenCalledWith({ message: 'ATM information not found' });
    });

    it('should return correct coordinates', async () => {
      const req = mockRequest({}, { id: testATM._id.toString() });
      const res = mockResponse();

      await getSpecificATM(req, res);

      const result = res.json.mock.calls[0][0];
      expect(result.coordinates.latitude).toBe(validATMData.coordinates.latitude);
      expect(result.coordinates.longitude).toBe(validATMData.coordinates.longitude);
    });

    it('should return correct timings', async () => {
      const req = mockRequest({}, { id: testATM._id.toString() });
      const res = mockResponse();

      await getSpecificATM(req, res);

      const result = res.json.mock.calls[0][0];
      expect(result.timings.monFri).toBe(validATMData.timings.monFri);
      expect(result.timings.satSun).toBe(validATMData.timings.satSun);
      expect(result.timings.holidays).toBe(validATMData.timings.holidays);
    });
  });
});
