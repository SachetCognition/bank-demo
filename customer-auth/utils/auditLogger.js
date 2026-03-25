import mongoose from 'mongoose';

const auditLogSchema = mongoose.Schema({
  timestamp: { type: Date, default: Date.now },
  action: { type: String, required: true },
  user_email: { type: String, required: true },
  details: { type: Object },
  ip_address: { type: String },
  service_name: { type: String, default: 'customer-auth' },
});

const AuditLog = mongoose.model('AuditLog', auditLogSchema);

const logAudit = async (action, userEmail, details, ipAddress = 'unknown') => {
  try {
    await AuditLog.create({
      action,
      user_email: userEmail,
      details,
      ip_address: ipAddress,
      service_name: 'customer-auth',
    });
  } catch (error) {
    console.error('Failed to write audit log:', error);
  }
};

export default logAudit;
