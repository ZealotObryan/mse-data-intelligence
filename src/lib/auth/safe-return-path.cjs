function isControlCharacter(value) {
  return /[\u0000-\u001f\u007f]/.test(value);
}

function safeReturnPath(value) {
  if (
    typeof value !== "string" ||
    !value.startsWith("/") ||
    value.startsWith("//") ||
    value.includes("\\") ||
    isControlCharacter(value)
  ) {
    return "/";
  }

  let decoded;
  let parsed;
  try {
    decoded = decodeURIComponent(value);
    parsed = new URL(value, "https://mse.invalid");
  } catch {
    return "/";
  }

  if (
    decoded.startsWith("//") ||
    decoded.includes("\\") ||
    isControlCharacter(decoded) ||
    parsed.origin !== "https://mse.invalid"
  ) {
    return "/";
  }

  return value;
}

module.exports = { safeReturnPath };
