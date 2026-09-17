import type { FastifyInstance } from 'fastify';
import type { Db } from '../db/index.js';
import { createSource, listSources, deleteSource } from '../sources.js';
import { requireUser } from '../auth.js';
import type { SourceConfig } from '../types.js';

export interface SourcesRouteOptions {
  db: Db;
  jwtSecret: string;
}

export function registerSourcesRoutes(app: FastifyInstance, { db, jwtSecret }: SourcesRouteOptions): void {
  app.get('/api/sources', async (req, reply) => {
    const user = requireUser(req, db, jwtSecret);
    if (!user) return reply.code(401).send({ error: 'not authenticated' });
    return reply.send(listSources(db, user.id));
  });

  app.post<{ Body: { kind: SourceConfig['kind']; config: Record<string, unknown> } }>('/api/sources', async (req, reply) => {
    const user = requireUser(req, db, jwtSecret);
    if (!user) return reply.code(401).send({ error: 'not authenticated' });

    const { kind, config } = req.body;
    if (!kind || !config) return reply.code(400).send({ error: 'kind and config are required' });

    const source = createSource(db, user.id, kind, config);
    return reply.code(201).send(source);
  });

  app.delete<{ Params: { id: string } }>('/api/sources/:id', async (req, reply) => {
    const user = requireUser(req, db, jwtSecret);
    if (!user) return reply.code(401).send({ error: 'not authenticated' });

    const deleted = deleteSource(db, user.id, req.params.id);
    if (!deleted) return reply.code(404).send({ error: 'source not found' });
    return reply.send({ ok: true });
  });
}
