import crypto from "crypto";

const generateCsrfToken = (req, res) => {
  const token = crypto.randomBytes(32).toString("hex");
  // Double-submit cookie pattern: store token in a non-httpOnly cookie
  // and return it in the response body. Client sends it back as a header.
  res.cookie("csrf_token", token, {
    httpOnly: false,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    maxAge: 3600000, // 1 hour
  });
  res.json({ csrfToken: token });
};

const validateCsrf = (req, res, next) => {
  // Skip CSRF for GET, HEAD, OPTIONS
  if (["GET", "HEAD", "OPTIONS"].includes(req.method)) {
    return next();
  }

  const headerToken = req.headers["x-csrf-token"] || req.body?._csrf;
  const cookieToken = req.cookies?.csrf_token;

  if (!headerToken || !cookieToken || headerToken !== cookieToken) {
    res.status(403);
    return res.json({ message: "Invalid or missing CSRF token" });
  }

  next();
};

export { generateCsrfToken, validateCsrf };
