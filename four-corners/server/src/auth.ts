/**
 * Two distinct credential types, deliberately not unified:
 * - a web session JWT (short-lived, cookie-carried) authenticates the *user* in the browser.
 * - a device credential secret (long-lived, Bearer header) authenticates the *worker* binary.
 * Conflating them would let a stolen browser cookie impersonate a device, or
 * vice versa — kept separate so each can be revoked independently.
 */

import jwt from 'jsonwebtoken';
import type { FastifyRequest } from 'fastify';
import type { Db } from './db/index.js';
import { authenticateDevice } from './pairing.js';
import { getUserById } from './users.js';
import type { Device, User } from './types.js';

const SESSION_TTL = '7d';

export interface SessionPayload {
  userId: string;
}

export function signSessionToken(userId: string, secret: string): string {
  return jwt.sign({ userId } satisfies SessionPayload, secret, { expiresIn: SESSION_TTL });
}

export function verifySessionToken(token: string, secret: string): SessionPayload | undefined {
  try {
    const decoded = jwt.verify(token, secret);
    if (typeof decoded === 'object' && decoded !== null && 'userId' in decoded) {
      return { userId: String((decoded as { userId: unknown }).userId) };
    }
    return undefined;
  } catch {
    return undefined;
  }
}

/** Resolves the authenticated User from the `session` cookie, or undefined. */
export function requireUser(req: FastifyRequest, db: Db, jwtSecret: string): User | undefined {
  const token = req.cookies?.session;
  if (!token) return undefined;
  const payload = verifySessionToken(token, jwtSecret);
  if (!payload) return undefined;
  return getUserById(db, payload.userId);
}

/** Resolves the authenticated Device from the `Authorization: Bearer <secret>` header, or undefined. */
export function requireDevice(req: FastifyRequest, db: Db): Device | undefined {
  const header = req.headers.authorization;
  if (!header?.startsWith('Bearer ')) return undefined;
  const secret = header.slice('Bearer '.length);
  return authenticateDevice(db, secret);
}
