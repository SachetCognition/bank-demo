# EU Regulatory Compliance Documentation

## Overview

This document describes the regulatory compliance features implemented in Martian Bank and identifies remaining gaps for full EU financial regulation compliance.

## Implemented Features

### PSD2 (Payment Services Directive 2)

#### Strong Customer Authentication (SCA)
- **Status**: Foundation implemented
- **Implementation**: TOTP-based 2FA (possession factor) combined with password (knowledge factor)
- **Endpoints**:
  - `POST /api/users/2fa/setup` — Generate TOTP secret
  - `POST /api/users/2fa/verify` — Verify and enable 2FA
- **Gap**: Missing biometric factor option; missing device binding

#### Transaction Monitoring
- **Status**: Basic implementation
- **Implementation**: Automated monitoring for:
  - High-value transactions (> 10,000 EUR)
  - High-frequency transactions (> 5/hour per account)
  - Self-transfers
- **Gap**: Missing ML-based anomaly detection; missing regulatory reporting integration

#### Transaction Limits
- **Status**: Implemented
- **Implementation**:
  - Per-transaction limit: 25,000 EUR (configurable)
  - Daily limit: 50,000 EUR (configurable)
  - Per-account overrides via `transaction_limits` collection

### GDPR (General Data Protection Regulation)

#### Right to Data Portability (Article 20)
- **Status**: Implemented
- **Endpoint**: `GET /api/users/data-export`
- **Format**: JSON download of all personal data
- **Gap**: Missing structured machine-readable format (e.g., CSV); missing data from all microservices

#### Right to Erasure (Article 17)
- **Status**: Implemented
- **Endpoint**: `DELETE /api/users/data-erasure`
- **Implementation**: Anonymization of PII while retaining financial records
- **Gap**: Cross-service data erasure needs orchestration layer

#### Audit Trail (Article 30)
- **Status**: Implemented
- **Implementation**: Immutable audit log in MongoDB with:
  - Timestamp, action, user, details, IP address, service name
- **Gap**: Missing data retention policies; missing scheduled purging

### AML (Anti-Money Laundering Directive)

#### Transaction Monitoring
- **Status**: Basic implementation
- **Implementation**: Rule-based monitoring with suspicious transaction flagging
- **Collection**: `suspicious_transactions` in MongoDB
- **Gap**: Missing Suspicious Activity Report (SAR) generation; missing regulatory body integration

### Data Protection

#### Encryption at Rest
- **Status**: Implemented for sensitive fields
- **Implementation**: AES-256 encryption for government ID numbers
- **Gap**: Full database encryption not implemented; key rotation needs automation

## Remaining Gaps for Full Compliance

### PSD2
1. Device binding and dynamic linking for transactions
2. Exemption management (trusted beneficiaries, low-value)
3. Regulatory reporting API integration
4. Open Banking API (AISP/PISP) interfaces

### GDPR
1. Consent management system
2. Data Processing Agreement (DPA) framework
3. Data Protection Impact Assessment (DPIA)
4. Cross-border data transfer mechanisms
5. Privacy by design in all new features
6. Cookie consent management

### AML / KYC
1. Know Your Customer (KYC) identity verification
2. Suspicious Activity Report (SAR) generation
3. Politically Exposed Persons (PEP) screening
4. Sanctions list checking
5. Customer Due Diligence (CDD) workflows

### MiFID II (if applicable)
1. Best execution reporting
2. Transaction reporting to competent authorities
3. Product governance requirements

### Operational Resilience
1. Incident reporting framework
2. Business continuity planning
3. Third-party risk management
4. ICT risk management (DORA compliance)

## Architecture Considerations

For full compliance, the following architectural changes are recommended:

1. **Event Sourcing**: Migrate from direct MongoDB writes to event sourcing for complete audit trail
2. **API Gateway**: Centralize authentication, rate limiting, and monitoring
3. **Dedicated Compliance Service**: Separate microservice for regulatory reporting
4. **Encryption at Rest**: Enable MongoDB encrypted storage engine
5. **Key Management**: Integrate with HSM or cloud KMS for key management
