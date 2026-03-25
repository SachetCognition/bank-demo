import crypto from "crypto";

const csrfTokens = new Map();

const generateCsrfToken = (req, res) => {
  const token = crypto.randomBytes(32).toString("hex");
  const sessionId = req.cookies?.jwt || req.ip;
  csrfTokens.set(sessionId, { token, expires: Date.now() + 3600000 }); // 1 hour expiry
  res.json({ csrfToken: token });
};

const validateCsrf = (req, res, next) => {
  // Skip CSRF for GET, HEAD, OPTIONS
  if (["GET", "HEAD", "OPTIONS"].includes(req.method)) {
    return next();
  }

  const csrfToken =
    req.headers["x-csrf-token"] || req.body?._csrf;
  const sessionId = req.cookies?.jwt || req.ip;
  const stored = csrfTokens.get(sessionId);

  if (!stored || stored.token !== csrfToken || stored.expires < Date.now()) {
    res.status(403);
    return res.json({ message: "Invalid or missing CSRF token" });
  }

  next();
};

// Cleanup expired tokens periodically
setInterval(() => {
  const now = Date.now();
  for (const [key, value] of csrfTokens.entries()) {
    if (value.expires < now) {
      csrfTokens.delete(key);
    }
  }
}, 3600000); // Cleanup every hour

export { generateCsrfToken, validateCsrf };
