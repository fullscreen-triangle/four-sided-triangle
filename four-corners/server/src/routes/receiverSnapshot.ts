import type { FastifyInstance } from 'fastify';
import type { Db } from '../db/index.js';
import { getSnapshot, putSnapshot } from '../receiverSnapshot.js';
import { requireDevice, requireUser } from '../auth.js';

export interface ReceiverSnapshotRouteOptions {
  db: Db;
  jwtSecret: string;
}

interface SnapshotBody {
  receiverId: string;
  committedCount: number;
  claims: string[];
  edges: Array<{ a: string; b: string; weight: number }>;
  expectedVersion?: number;
}

export function registerReceiverSnapshotRoutes(app: FastifyInstance, { db, jwtSecret }: ReceiverSnapshotRouteOptions): void {
  // Worker pull/push — authenticated by device credential, not user session.
  app.get('/api/receiver-snapshot', async (req, reply) => {
    const device = requireDevice(req, db);
    if (!device) return reply.code(401).send({ error: 'not authenticated' });

    const snapshot = getSnapshot(db, device.userId, device.id);
    if (!snapshot) return reply.code(404).send({ error: 'no snapshot yet' });
    return reply.send(snapshot);
  });

  app.put<{ Body: SnapshotBody }>('/api/receiver-snapshot', async (req, reply) => {
    const device = requireDevice(req, db);
    if (!device) return reply.code(401).send({ error: 'not authenticated' });

    const { expectedVersion, ...snapshot } = req.body;
    const result = putSnapshot(db, device.userId, device.id, snapshot, expectedVersion);
    if (!result.ok) {
      return reply.code(409).send({ error: result.reason, currentVersion: result.currentVersion });
    }
    return reply.send({ ok: true, version: result.version });
  });

  // Web UI read-only view of the worker's last-pushed state, per device.
  app.get<{ Params: { deviceId: string } }>('/api/devices/:deviceId/receiver-snapshot', async (req, reply) => {
    const user = requireUser(req, db, jwtSecret);
    if (!user) return reply.code(401).send({ error: 'not authenticated' });

    const snapshot = getSnapshot(db, user.id, req.params.deviceId);
    if (!snapshot) return reply.code(404).send({ error: 'no snapshot yet' });
    return reply.send(snapshot);
  });
}
