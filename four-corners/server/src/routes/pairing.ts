import type { FastifyInstance } from 'fastify';
import type { Db } from '../db/index.js';
import { issuePairingToken, redeemPairingToken, listDevices, revokeDevice } from '../pairing.js';
import { requireUser } from '../auth.js';

export interface PairingRouteOptions {
  db: Db;
  jwtSecret: string;
}

export function registerPairingRoutes(app: FastifyInstance, { db, jwtSecret }: PairingRouteOptions): void {
  // Web UI: "Connect a device" — issues a short-lived, one-time code to show the user.
  app.post('/api/pairing-tokens', async (req, reply) => {
    const user = requireUser(req, db, jwtSecret);
    if (!user) return reply.code(401).send({ error: 'not authenticated' });

    const issued = issuePairingToken(db, user.id);
    return reply.code(201).send({ code: issued.code, expiresAt: issued.expiresAt });
  });

  // Worker: redeems a code typed by the user, gets back a long-lived device credential.
  app.post<{ Body: { code: string; deviceName: string } }>('/api/pairing-tokens/redeem', async (req, reply) => {
    const { code, deviceName } = req.body;
    if (!code || !deviceName) {
      return reply.code(400).send({ error: 'code and deviceName are required' });
    }

    const result = redeemPairingToken(db, code.toUpperCase(), deviceName);
    if (!result.ok) {
      const statusByReason = { 'not-found': 404, expired: 410, 'already-used': 409, revoked: 403 } as const;
      return reply.code(statusByReason[result.reason]).send({ error: result.reason });
    }

    return reply.code(201).send({
      deviceId: result.device.id,
      deviceCredential: result.deviceCredentialSecret
    });
  });

  app.get('/api/devices', async (req, reply) => {
    const user = requireUser(req, db, jwtSecret);
    if (!user) return reply.code(401).send({ error: 'not authenticated' });
    return reply.send(listDevices(db, user.id));
  });

  app.delete<{ Params: { id: string } }>('/api/devices/:id', async (req, reply) => {
    const user = requireUser(req, db, jwtSecret);
    if (!user) return reply.code(401).send({ error: 'not authenticated' });

    const revoked = revokeDevice(db, user.id, req.params.id);
    if (!revoked) return reply.code(404).send({ error: 'device not found' });
    return reply.send({ ok: true });
  });
}
