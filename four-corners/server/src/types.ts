export interface User {
  id: string;
  email: string;
  passwordHash: string;
  createdAt: string;
}

export interface SourceConfig {
  id: string;
  userId: string;
  kind: 'local-file' | 'api';
  /** Opaque to the server — interpreted by the worker. For 'local-file', e.g. { root, extensions }. Never file contents. */
  config: Record<string, unknown>;
  createdAt: string;
}

export type PairingTokenStatus = 'pending' | 'paired' | 'expired' | 'revoked';

export interface PairingToken {
  id: string;
  userId: string;
  codeHash: string;
  status: PairingTokenStatus;
  createdAt: string;
  expiresAt: string;
  redeemedAt: string | null;
}

export interface Device {
  id: string;
  userId: string;
  deviceName: string;
  deviceKeyHash: string;
  pairedAt: string;
  lastSeenAt: string | null;
  revokedAt: string | null;
}

/** Matches sdk-ts's ReceiverSnapshot shape exactly (four-sided-triangle/sdk-ts/src/receiver.ts) — this table is a PersistAdapter target over HTTP. */
export interface ReceiverSnapshotRecord {
  userId: string;
  deviceId: string;
  receiverId: string;
  committedCount: number;
  claims: string[];
  edges: Array<{ a: string; b: string; weight: number }>;
  version: number;
  updatedAt: string;
}
