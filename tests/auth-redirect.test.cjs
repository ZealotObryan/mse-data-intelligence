const test = require("node:test");
const assert = require("node:assert/strict");
const { safeReturnPath } = require("../src/lib/auth/safe-return-path.cjs");

test("keeps safe local paths and query strings", () => {
  assert.equal(safeReturnPath("/"), "/");
  assert.equal(safeReturnPath("/market?tab=overview"), "/market?tab=overview");
  assert.equal(safeReturnPath("/company/ABC#financials"), "/company/ABC#financials");
});

test("rejects absolute and protocol-relative destinations", () => {
  assert.equal(safeReturnPath("https://evil.example"), "/");
  assert.equal(safeReturnPath("//evil.example/path"), "/");
  assert.equal(safeReturnPath("javascript:alert(1)"), "/");
});

test("rejects backslash-based and encoded protocol-relative destinations", () => {
  assert.equal(safeReturnPath("/\\\\evil.example"), "/");
  assert.equal(safeReturnPath("/%5c%5cevil.example"), "/");
  assert.equal(safeReturnPath("/%2f%2fevil.example"), "/");
});

test("rejects malformed encodings and control characters", () => {
  assert.equal(safeReturnPath("/%E0%A4%A"), "/");
  assert.equal(safeReturnPath("/market\nLocation: https://evil.example"), "/");
});

test("rejects missing and non-string values", () => {
  assert.equal(safeReturnPath(null), "/");
  assert.equal(safeReturnPath(undefined), "/");
  assert.equal(safeReturnPath(42), "/");
  assert.equal(safeReturnPath(""), "/");
});
