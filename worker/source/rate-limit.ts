// Per-IP fixed-window rate limit backed by Workers KV — a 1-hour and a
// 24-hour bucket, rejected when either is exhausted. KV's eventual
// consistency is acceptable; worst case is a small overshoot before reset.

/**
 * Per-IP request budget — max calls allowed in each fixed window.
 */
export interface Limits {
  perHour: number;
  perDay: number;
}

// One hour in seconds — short-window bucket size.
const HOUR = 3600;
// One day in seconds — long-window bucket size.
const DAY = 86400;

/**
 * Charge one request against the IP's hour and day buckets in KV.
 * Returns a 429 Response when either bucket is exhausted, null on success.
 */
export async function rateLimit(
  kv: KVNamespace | undefined, ip: string, limits: Limits = { perHour: 30, perDay: 100 }
): Promise<Response | null> {
  if (!kv) {
    return null; // dev-mode fallback when KV isn't bound
  }
  const hour_key = `rl:h:${ip}:${Math.floor(Date.now() / 1000 / HOUR)}`;
  const day_key = `rl:d:${ip}:${Math.floor(Date.now() / 1000 / DAY)}`;
  const [hour_txt, day_txt] = await Promise.all([
    kv.get(hour_key),
    kv.get(day_key),
  ]);
  const hour = (hour_txt ? parseInt(hour_txt, 10) : 0) + 1;
  const day = (day_txt ? parseInt(day_txt, 10) : 0) + 1;
  if (hour > limits.perHour) {
    return tooMany(HOUR);
  }
  if (day > limits.perDay) {
    return tooMany(DAY);
  }
  await Promise.all([
    kv.put(hour_key, String(hour), { expirationTtl: HOUR + 60 }),
    kv.put(day_key, String(day), { expirationTtl: DAY + 60 }),
  ]);
  return null;
}

/**
 * Build the 429 response with a stable error code and Retry-After header.
 */
function tooMany(retry_after: number): Response {
  return new Response(
    JSON.stringify({
      error: 'rate_limited', retry_after_sec: retry_after
    }),
    {
      status: 429,
      headers: {
        'content-type': 'application/json',
        'retry-after': String(retry_after),
      },
    }
  );
}

export default rateLimit;
