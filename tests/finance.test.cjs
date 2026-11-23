const test = require("node:test");
const assert = require("node:assert/strict");
const {
  calculatePriceReturnPercent,
  calculateMarketValue,
  calculateWeightedAverageCost,
  roundMoney,
} = require("../src/lib/finance/decimal.cjs");

test("calculates percentage returns without binary floating-point drift", () => {
  assert.equal(calculatePriceReturnPercent("0.1", "0.3").toString(), "200");
  assert.equal(calculatePriceReturnPercent("100", "112").toString(), "12");
  assert.equal(calculatePriceReturnPercent("100", "95").toString(), "-5");
});

test("calculates market value exactly from decimal strings", () => {
  assert.equal(calculateMarketValue("0.1", "0.2").toString(), "0.02");
  assert.equal(calculateMarketValue("1250", "86.35").toString(), "107937.5");
});

test("calculates weighted average cost across multiple purchases", () => {
  const average = calculateWeightedAverageCost([
    { quantity: "10", unitCost: "12.50" },
    { quantity: "5", unitCost: "13.10" },
  ]);
  assert.equal(average.toFixed(4), "12.7000");
});

test("rounds monetary values using half-up rounding", () => {
  assert.equal(roundMoney("12.345").toFixed(2), "12.35");
  assert.equal(roundMoney("12.344").toFixed(2), "12.34");
});

test("rejects invalid or unsafe financial inputs", () => {
  assert.throws(() => calculatePriceReturnPercent("0", "10"), /cannot be zero/);
  assert.throws(() => calculateMarketValue("-1", "10"), /cannot be negative/);
  assert.throws(() => calculateMarketValue("NaN", "10"), /finite decimal/);
  assert.throws(() => calculateWeightedAverageCost([{ quantity: "0", unitCost: "10" }]), /greater than zero/);
  assert.throws(() => roundMoney("1", 9), /between 0 and 8/);
});
