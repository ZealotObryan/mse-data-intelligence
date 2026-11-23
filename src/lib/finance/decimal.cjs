const Decimal = require("decimal.js");

Decimal.set({ precision: 40, rounding: Decimal.ROUND_HALF_UP });

function asDecimal(value, label) {
  let result;
  try {
    result = new Decimal(value);
  } catch {
    throw new TypeError(`${label} must be a valid finite decimal value`);
  }
  if (!result.isFinite()) {
    throw new TypeError(`${label} must be a valid finite decimal value`);
  }
  return result;
}

function nonNegative(value, label) {
  const result = asDecimal(value, label);
  if (result.isNegative()) throw new RangeError(`${label} cannot be negative`);
  return result;
}

function calculatePriceReturnPercent(startPrice, endPrice) {
  const start = asDecimal(startPrice, "startPrice");
  const end = asDecimal(endPrice, "endPrice");
  if (start.isZero()) throw new RangeError("startPrice cannot be zero");
  return end.minus(start).div(start).times(100);
}

function calculateMarketValue(quantity, price) {
  return nonNegative(quantity, "quantity").times(nonNegative(price, "price"));
}

function calculateWeightedAverageCost(positions) {
  if (!Array.isArray(positions) || positions.length === 0) {
    throw new TypeError("positions must be a non-empty array");
  }
  let totalQuantity = new Decimal(0);
  let totalCost = new Decimal(0);
  for (const [index, position] of positions.entries()) {
    if (!position || typeof position !== "object") {
      throw new TypeError(`positions[${index}] must contain quantity and unitCost`);
    }
    const quantity = nonNegative(position.quantity, `positions[${index}].quantity`);
    const unitCost = nonNegative(position.unitCost, `positions[${index}].unitCost`);
    totalQuantity = totalQuantity.plus(quantity);
    totalCost = totalCost.plus(quantity.times(unitCost));
  }
  if (totalQuantity.isZero()) throw new RangeError("total quantity must be greater than zero");
  return totalCost.div(totalQuantity);
}

function roundMoney(value, decimalPlaces = 2) {
  if (!Number.isInteger(decimalPlaces) || decimalPlaces < 0 || decimalPlaces > 8) {
    throw new RangeError("decimalPlaces must be an integer between 0 and 8");
  }
  return asDecimal(value, "value").toDecimalPlaces(decimalPlaces, Decimal.ROUND_HALF_UP);
}

module.exports = {
  Decimal,
  asDecimal,
  calculatePriceReturnPercent,
  calculateMarketValue,
  calculateWeightedAverageCost,
  roundMoney,
};
