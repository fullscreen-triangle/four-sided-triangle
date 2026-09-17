import Fastify from 'fastify';
import cookie from '@fastify/cookie';
import { openDb } from './db/index.js';
import { registerAuthRoutes } from './routes/auth.js';
import { registerPairingRoutes } from './routes/pairing.js';
import { registerSourcesRoutes } from './routes/sources.js';
import { registerReceiverSnapshotRoutes } from './routes/receiverSnapshot.js';

/** Builds (but does not start listening on) a fully-wired Fastify app. Side-effect-free — safe to import from tests. */
export async function buildServer(jwtSecret: string, dbPath: string, logger = true) {
  const db = openDb(dbPath);
  const app = Fastify({ logger });

  await app.register(cookie);

  app.get('/health', async () => ({ status: 'ok' }));

  registerAuthRoutes(app, { db, jwtSecret });
  registerPairingRoutes(app, { db, jwtSecret });
  registerSourcesRoutes(app, { db, jwtSecret });
  registerReceiverSnapshotRoutes(app, { db, jwtSecret });

  return app;
}
