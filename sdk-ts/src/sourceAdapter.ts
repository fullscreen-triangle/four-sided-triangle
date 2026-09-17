/**
 * Source adapters (paper Remark 2.2: no boundary between local, remote, and
 * learned — all are computationally uniform contents of the medium prior to
 * individuation). A `SourceAdapter` yields claims as chunks of text with a
 * stable id; the federation layer (federation.ts) unions adapters as one
 * contact graph per Def 8.1.
 */

export interface SourceChunk {
  /** Stable id, unique within this adapter — becomes the claim id in the contact graph. */
  id: string;
  text: string;
  /** Human-readable origin, e.g. a file path — never shown as "the answer," only as provenance. */
  origin: string;
}

export interface SourceAdapter {
  /** A name for this adapter, used as the catalyst `source` field (Def 6.1) for independence checks. */
  readonly name: string;
  /** Yield every claim this source can currently offer. Called once per federation build. */
  list(): Promise<SourceChunk[]>;
}

/** A source built directly from in-memory chunks — useful for tests and for wrapping any existing index. */
export class InMemorySource implements SourceAdapter {
  constructor(
    readonly name: string,
    private readonly chunks: SourceChunk[],
  ) {}

  async list(): Promise<SourceChunk[]> {
    return this.chunks;
  }
}
