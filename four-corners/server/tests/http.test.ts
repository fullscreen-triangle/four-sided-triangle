import { describe, it, expect, beforeEach } from 'vitest';
import type { FastifyInstance } from 'fastify';
import { buildServer } from '../src/index.js';

/**
 * End-to-end HTTP smoke test: signup, login, issue a pairing token, redeem
 * it as a worker would, authenticate as that device, push+pull a receiver
 * snapshot. Exercises the actual routes, not just the underlying functions.
 */
describe('four-corners server — HTTP flow', () => {
  let app: FastifyInstance;

  beforeEach(async () => {
    app = await buildServer('test-secret-not-for-production', ':memory:', false);
  });

  function extractSessionCookie(setCookieHeader: string | string[] | undefined): string {
    const header = Array.isArray(setCookieHeader) ? setCookieHeader[0] : setCookieHeader;
    const match = header?.match(/session=([^;]+)/);
    if (!match) throw new Error('no session cookie set');
    return `session=${match[1]}`;
  }

  it('signs up, logs in, and reads /api/auth/me', async () => {
    const signupRes = await app.inject({
      method: 'POST',
      url: '/api/auth/signup',
      payload: { email: 'user@example.com', password: 'correct horse battery staple' }
    });
    expect(signupRes.statusCode).toBe(201);
    const cookie = extractSessionCookie(signupRes.headers['set-cookie']);

    const meRes = await app.inject({ method: 'GET', url: '/api/auth/me', headers: { cookie } });
    expect(meRes.statusCode).toBe(200);
    expect(meRes.json().email).toBe('user@example.com');
  });

  it('rejects duplicate signup emails', async () => {
    await app.inject({ method: 'POST', url: '/api/auth/signup', payload: { email: 'dup@example.com', password: 'a real password 1' } });
    const second = await app.inject({ method: 'POST', url: '/api/auth/signup', payload: { email: 'dup@example.com', password: 'another password 2' } });
    expect(second.statusCode).toBe(409);
  });

  it('full pairing flow: issue token -> worker redeems -> device authenticates -> pushes and pulls a snapshot', async () => {
    const signupRes = await app.inject({
      method: 'POST',
      url: '/api/auth/signup',
      payload: { email: 'researcher@example.com', password: 'correct horse battery staple' }
    });
    const cookie = extractSessionCookie(signupRes.headers['set-cookie']);

    const issueRes = await app.inject({ method: 'POST', url: '/api/pairing-tokens', headers: { cookie } });
    expect(issueRes.statusCode).toBe(201);
    const { code } = issueRes.json() as { code: string };

    const redeemRes = await app.inject({
      method: 'POST',
      url: '/api/pairing-tokens/redeem',
      payload: { code, deviceName: 'test-laptop' }
    });
    expect(redeemRes.statusCode).toBe(201);
    const { deviceCredential } = redeemRes.json() as { deviceId: string; deviceCredential: string };

    // Redeeming the same code again must fail.
    const secondRedeem = await app.inject({
      method: 'POST',
      url: '/api/pairing-tokens/redeem',
      payload: { code, deviceName: 'someone-elses-laptop' }
    });
    expect(secondRedeem.statusCode).toBe(409);

    // Web UI sees the paired device.
    const devicesRes = await app.inject({ method: 'GET', url: '/api/devices', headers: { cookie } });
    expect(devicesRes.json()).toHaveLength(1);
    expect(devicesRes.json()[0].deviceName).toBe('test-laptop');

    // Worker pushes a snapshot using its device credential.
    const pushRes = await app.inject({
      method: 'PUT',
      url: '/api/receiver-snapshot',
      headers: { authorization: `Bearer ${deviceCredential}` },
      payload: { receiverId: 'r1', committedCount: 3, claims: ['a', 'b'], edges: [] }
    });
    expect(pushRes.statusCode).toBe(200);
    expect(pushRes.json().version).toBe(1);

    // Worker pulls it back.
    const pullRes = await app.inject({
      method: 'GET',
      url: '/api/receiver-snapshot',
      headers: { authorization: `Bearer ${deviceCredential}` }
    });
    expect(pullRes.statusCode).toBe(200);
    expect(pullRes.json().committedCount).toBe(3);

    // An unauthenticated request (no bearer token) is refused.
    const unauthedRes = await app.inject({ method: 'GET', url: '/api/receiver-snapshot' });
    expect(unauthedRes.statusCode).toBe(401);
  });

  it('sources CRUD is scoped to the authenticated user', async () => {
    const signupRes = await app.inject({ method: 'POST', url: '/api/auth/signup', payload: { email: 'a@example.com', password: 'password number one' } });
    const cookieA = extractSessionCookie(signupRes.headers['set-cookie']);

    const createRes = await app.inject({
      method: 'POST',
      url: '/api/sources',
      headers: { cookie: cookieA },
      payload: { kind: 'local-file', config: { root: '/home/user/docs' } }
    });
    expect(createRes.statusCode).toBe(201);

    const otherSignup = await app.inject({ method: 'POST', url: '/api/auth/signup', payload: { email: 'b@example.com', password: 'password number two' } });
    const cookieB = extractSessionCookie(otherSignup.headers['set-cookie']);

    const listAsB = await app.inject({ method: 'GET', url: '/api/sources', headers: { cookie: cookieB } });
    expect(listAsB.json()).toHaveLength(0);

    const listAsA = await app.inject({ method: 'GET', url: '/api/sources', headers: { cookie: cookieA } });
    expect(listAsA.json()).toHaveLength(1);
  });
});
