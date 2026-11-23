const Decimal = require("decimal.js");
const DATE_ONLY = /^\d{4}-\d{2}-\d{2}$/;

function validDate(value) {
  if (typeof value !== "string" || !DATE_ONLY.test(value)) return false;
  const date = new Date(value + "T00:00:00.000Z");
  return !Number.isNaN(date.getTime()) && date.toISOString().slice(0, 10) === value;
}
function decimalOrNull(value, field, rules = {}) {
  if (value === null || value === undefined || value === "") return null;
  let parsed;
  try { parsed = new Decimal(value); } catch { throw new TypeError(field + " must be a finite decimal string or null"); }
  if (!parsed.isFinite()) throw new TypeError(field + " must be a finite decimal string or null");
  if (rules.nonNegative && parsed.isNegative()) throw new RangeError(field + " cannot be negative");
  if (rules.positive && !parsed.isPositive()) throw new RangeError(field + " must be greater than zero");
  return parsed;
}
/**
 * Normalize daily OHLCV records without manufacturing observations.
 * Duplicate dates use the last valid input record. Missing sessions are only
 * reported when the caller supplies an authoritative expectedSessions calendar.
 */
function normalizeDailyBars(records, options = {}) {
  if (!Array.isArray(records)) throw new TypeError("records must be an array");
  const expectedSessions = options.expectedSessions;
  if (expectedSessions !== undefined && (!Array.isArray(expectedSessions) || expectedSessions.some(d => !validDate(d)))) {
    throw new TypeError("expectedSessions must contain valid YYYY-MM-DD dates");
  }
  const rejected = [], byDate = new Map();
  let duplicates = 0;
  records.forEach((record, index) => {
    try {
      if (!record || typeof record !== "object" || Array.isArray(record)) throw new TypeError("record must be an object");
      if (!validDate(record.date)) throw new TypeError("date must be a real YYYY-MM-DD calendar date");
      const open = decimalOrNull(record.open, "open", { positive: true });
      const high = decimalOrNull(record.high, "high", { positive: true });
      const low = decimalOrNull(record.low, "low", { positive: true });
      const close = decimalOrNull(record.close, "close", { positive: true });
      const volume = decimalOrNull(record.volume, "volume", { nonNegative: true });
      if ([open, high, low, close].some(v => v === null)) throw new TypeError("open, high, low and close are required; incomplete candles are not published");
      if (high.lessThan(low)) throw new RangeError("high cannot be below low");
      if (high.lessThan(open) || high.lessThan(close) || low.greaterThan(open) || low.greaterThan(close)) {
        throw new RangeError("open and close must fall within the low/high range");
      }
      if (byDate.has(record.date)) duplicates += 1;
      byDate.set(record.date, {
        date: record.date, open: open.toString(), high: high.toString(),
        low: low.toString(), close: close.toString(),
        volume: volume === null ? null : volume.toString(),
        sourceRecordId: record.sourceRecordId ?? null,
      });
    } catch (error) { rejected.push({ index, reason: error.message }); }
  });
  const bars = [...byDate.values()].sort((a, b) => a.date.localeCompare(b.date));
  const missingSessions = expectedSessions === undefined ? null :
    [...new Set(expectedSessions)].filter(date => !byDate.has(date)).sort();
  return { bars, rejected, duplicates, missingSessions };
}
module.exports = { normalizeDailyBars, validDate };
