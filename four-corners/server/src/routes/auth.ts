import type { FastifyInstance } from 'fastify';
import type { Db } from '../db/index.js';
import { signup, login } from '../users.js';
import { signSessionToken, requireUser } from '../auth.js';

export interface AuthRouteOptions {
  db: Db;
  jwtSecret: string;
}

export function registerAuthRoutes(app: FastifyInstance, { db, jwtSecret }: AuthRouteOptions): void {
  app.post<{ Body: { email: string; password: string } }>('/api/auth/signup', async (req, reply) => {
    const { email, password } = req.body;
    if (!email || !password || password.length < 8) {
      return reply.code(400).send({ error: 'email and a password of at least 8 characters are required' });
    }

    const result = await signup(db, email, password);
    if (!result.ok) {
      return reply.code(409).send({ error: result.reason });
    }

    const token = signSessionToken(result.user.id, jwtSecret);
    void reply.setCookie('session', token, { httpOnly: true, sameSite: 'lax', path: '/' });
    return reply.code(201).send({ id: result.user.id, email: result.user.email });
  });

  app.post<{ Body: { email: string; password: string } }>('/api/auth/login', async (req, reply) => {
    const { email, password } = req.body;
    const result = await login(db, email ?? '', password ?? '');
    if (!result.ok) {
      return reply.code(401).send({ error: result.reason });
    }

    const token = signSessionToken(result.user.id, jwtSecret);
    void reply.setCookie('session', token, { httpOnly: true, sameSite: 'lax', path: '/' });
    return reply.send({ id: result.user.id, email: result.user.email });
  });

  app.post('/api/auth/logout', async (_req, reply) => {
    void reply.clearCookie('session', { path: '/' });
    return reply.send({ ok: true });
  });

  app.get('/api/auth/me', async (req, reply) => {
    const user = requireUser(req, db, jwtSecret);
    if (!user) return reply.code(401).send({ error: 'not authenticated' });
    return reply.send({ id: user.id, email: user.email });
  });
}
