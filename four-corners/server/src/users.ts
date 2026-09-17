import { randomUUID } from 'node:crypto';
import argon2 from 'argon2';
import type { Db } from './db/index.js';
import type { User } from './types.js';

interface UserRow {
  id: string;
  email: string;
  password_hash: string;
  created_at: string;
}

function rowToUser(row: UserRow): User {
  return { id: row.id, email: row.email, passwordHash: row.password_hash, createdAt: row.created_at };
}

export type SignupResult = { ok: true; user: User } | { ok: false; reason: 'email-taken' };

export async function signup(db: Db, email: string, password: string): Promise<SignupResult> {
  const existing = db.prepare(`SELECT id FROM users WHERE email = ?`).get(email);
  if (existing) return { ok: false, reason: 'email-taken' };

  const passwordHash = await argon2.hash(password);
  const id = randomUUID();
  db.prepare(`INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)`).run(id, email, passwordHash);

  const row = db.prepare(`SELECT * FROM users WHERE id = ?`).get(id) as UserRow;
  return { ok: true, user: rowToUser(row) };
}

export type LoginResult = { ok: true; user: User } | { ok: false; reason: 'invalid-credentials' };

export async function login(db: Db, email: string, password: string): Promise<LoginResult> {
  const row = db.prepare(`SELECT * FROM users WHERE email = ?`).get(email) as UserRow | undefined;
  if (!row) return { ok: false, reason: 'invalid-credentials' };

  const valid = await argon2.verify(row.password_hash, password);
  if (!valid) return { ok: false, reason: 'invalid-credentials' };

  return { ok: true, user: rowToUser(row) };
}

export function getUserById(db: Db, id: string): User | undefined {
  const row = db.prepare(`SELECT * FROM users WHERE id = ?`).get(id) as UserRow | undefined;
  return row ? rowToUser(row) : undefined;
}
