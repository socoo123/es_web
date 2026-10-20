export type Health = { status: 'UP'; service: 'travel-portal'; stage: 'F01' };

export async function getHealth(): Promise<Health> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), 3000);
  try {
    const response = await fetch('/api/health', { signal: controller.signal });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const body: unknown = await response.json();
    if (typeof body !== 'object' || body === null ||
        !('status' in body) || body.status !== 'UP' ||
        !('service' in body) || body.service !== 'travel-portal' ||
        !('stage' in body) || body.stage !== 'F01') {
      throw new Error('健康响应不符合 F01 契约');
    }
    return body as Health;
  } finally {
    window.clearTimeout(timer);
  }
}
