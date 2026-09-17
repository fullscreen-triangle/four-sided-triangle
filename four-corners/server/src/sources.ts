import { randomUUID } from 'node:crypto';
import type { Db } from './db/index.js';
import type { SourceConfig } from './types.js';

interface SourceRow {
  id: string;
  user_id: string;
  kind: string;
  config_json: string;
  created_at: string;
}

function rowToSource(row: SourceRow): SourceConfig {
  return {
    id: row.id,
    userId: row.user_id,
    kind: row.kind as SourceConfig['kind'],
    config: JSON.parse(row.config_json) as Record<string, unknown>,
    createdAt: row.created_at
  };
}

export function createSource(db: Db, userId: string, kind: SourceConfig['kind'], config: Record<string, unknown>): SourceConfig {
  const id = randomUUID();
  db.prepare(`INSERT INTO sources (id, user_id, kind, config_json) VALUES (?, ?, ?, ?)`).run(
    id,
    userId,
    kind,
    JSON.stringify(config)
  );
  const row = db.prepare(`SELECT * FROM sources WHERE id = ?`).get(id) as SourceRow;
  return rowToSource(row);
}

export function listSources(db: Db, userId: string): SourceConfig[] {
  const rows = db.prepare(`SELECT * FROM sources WHERE user_id = ? ORDER BY created_at DESC`).all(userId) as SourceRow[];
  return rows.map(rowToSource);
}

export function deleteSource(db: Db, userId: string, sourceId: string): boolean {
  const result = db.prepare(`DELETE FROM sources WHERE id = ? AND user_id = ?`).run(sourceId, userId);
  return result.changes > 0;
}
