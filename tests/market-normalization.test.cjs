const test = require("node:test");
const assert = require("node:assert/strict");
const { normalizeDailyBars, validDate } = require("../src/lib/market/normalize-bars.cjs");
const bar = (date, overrides = {}) => ({ date, open: "10.00", high: "12.00", low: "9.00", close: "11.00", volume: "100", ...overrides });

test("validates real calendar dates", () => {
  assert.equal(validDate("2026-02-28"), true);
  assert.equal(validDate("2026-02-30"), false);
  assert.equal(validDate("2026-2-03"), false);
});
test("sorts chronologically and preserves decimal values", () => {
  const result = normalizeDailyBars([bar("2026-01-06", { close: "10.10" }), bar("2026-01-05")]);
  assert.deepEqual(result.bars.map(x => x.date), ["2026-01-05", "2026-01-06"]);
  assert.equal(result.bars[1].close, "10.1");
  assert.equal(result.rejected.length, 0);
});
test("last valid duplicate wins; invalid later duplicates do not erase it", () => {
  const result = normalizeDailyBars([bar("2026-01-05", { close: "10.50" }), bar("2026-01-05", { close: "11.00" }), bar("2026-01-05", { close: "0" })]);
  assert.equal(result.duplicates, 1);
  assert.equal(result.bars.length, 1);
  assert.equal(result.bars[0].close, "11");
  assert.equal(result.rejected.length, 1);
});
test("preserves null volume and never invents missing candles", () => {
  const result = normalizeDailyBars([bar("2026-01-05", { volume: null })]);
  assert.equal(result.bars[0].volume, null);
  assert.equal(result.missingSessions, null);
});
test("reports gaps only against an authoritative supplied calendar", () => {
  const result = normalizeDailyBars([bar("2026-01-05"), bar("2026-01-07")], { expectedSessions: ["2026-01-05", "2026-01-06", "2026-01-07"] });
  assert.deepEqual(result.missingSessions, ["2026-01-06"]);
  assert.equal(normalizeDailyBars([bar("2026-01-05"), bar("2026-01-07")]).missingSessions, null);
});
test("rejects invalid dates, incomplete candles and invalid OHLCV", () => {
  const result = normalizeDailyBars([bar("2026-02-30"), bar("2026-01-06", { close: null }), bar("2026-01-07", { low: "13" }), bar("2026-01-08", { volume: "-1" }), bar("2026-01-09", { open: "NaN" })]);
  assert.equal(result.bars.length, 0);
  assert.equal(result.rejected.length, 5);
});
test("does not infer weekend or holiday gaps", () => {
  const result = normalizeDailyBars([bar("2026-01-09"), bar("2026-01-12")]);
  assert.deepEqual(result.bars.map(x => x.date), ["2026-01-09", "2026-01-12"]);
  assert.equal(result.missingSessions, null);
});
