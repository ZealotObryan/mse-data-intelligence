import Decimal = require("decimal.js");

export function asDecimal(value: Decimal.Value, label?: string): Decimal;
export function calculatePriceReturnPercent(startPrice: Decimal.Value, endPrice: Decimal.Value): Decimal;
export function calculateMarketValue(quantity: Decimal.Value, price: Decimal.Value): Decimal;
export function calculateWeightedAverageCost(positions: Array<{ quantity: Decimal.Value; unitCost: Decimal.Value }>): Decimal;
export function roundMoney(value: Decimal.Value, decimalPlaces?: number): Decimal;
