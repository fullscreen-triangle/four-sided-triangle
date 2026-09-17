/**
 * Reference SourceAdapter: local filesystem, plain text + optional PDF.
 * Chunks by paragraph (blank-line-delimited) with a minimum size, so a
 * claim is a genuine passage rather than a single sentence fragment or an
 * entire document (both of which would blur what "the passage" individuates).
 */

import { readFile, readdir, stat } from "node:fs/promises";
import { join, relative, extname } from "node:path";
import type { SourceAdapter, SourceChunk } from "../sourceAdapter.js";

export interface LocalFileSourceOptions {
  root: string;
  /** File extensions to include, e.g. [".md", ".txt", ".pdf"]. Default: text + pdf. */
  extensions?: string[];
  /** Minimum characters for a chunk to be kept as a claim (avoids noise fragments). */
  minChunkChars?: number;
  /** Maximum characters per chunk before it's split further. */
  maxChunkChars?: number;
}

const DEFAULT_EXTENSIONS = [".md", ".txt", ".mdx"];
const DEFAULT_MIN_CHARS = 80;
const DEFAULT_MAX_CHARS = 2000;

export class LocalFileSource implements SourceAdapter {
  readonly name = "local-file";
  private readonly opts: Required<LocalFileSourceOptions>;

  constructor(options: LocalFileSourceOptions) {
    this.opts = {
      root: options.root,
      extensions: options.extensions ?? DEFAULT_EXTENSIONS,
      minChunkChars: options.minChunkChars ?? DEFAULT_MIN_CHARS,
      maxChunkChars: options.maxChunkChars ?? DEFAULT_MAX_CHARS,
    };
  }

  async list(): Promise<SourceChunk[]> {
    const files = await this.walk(this.opts.root);
    const chunks: SourceChunk[] = [];
    for (const file of files) {
      const text = await this.readAsText(file);
      if (!text) continue;
      const rel = relative(this.opts.root, file).replace(/\\/g, "/");
      let index = 0;
      for (const para of this.chunkParagraphs(text)) {
        chunks.push({ id: `${rel}#${index}`, text: para, origin: rel });
        index++;
      }
    }
    return chunks;
  }

  private async walk(dir: string): Promise<string[]> {
    const entries = await readdir(dir, { withFileTypes: true });
    const out: string[] = [];
    for (const entry of entries) {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === "node_modules" || entry.name.startsWith(".")) continue;
        out.push(...(await this.walk(full)));
      } else if (this.opts.extensions.includes(extname(entry.name).toLowerCase())) {
        out.push(full);
      }
    }
    return out;
  }

  private async readAsText(file: string): Promise<string | null> {
    const ext = extname(file).toLowerCase();
    if (ext === ".pdf") {
      return this.readPdf(file);
    }
    const info = await stat(file);
    if (info.size === 0) return null;
    return readFile(file, "utf-8");
  }

  private async readPdf(file: string): Promise<string | null> {
    let pdfParse: (buf: Buffer) => Promise<{ text: string }>;
    try {
      // Optional peer dependency (package.json): only imported if the caller
      // actually points a LocalFileSource at .pdf files and has it installed.
      // A variable specifier keeps TS from resolving "pdf-parse"'s types
      // statically, since the package is never a required dependency.
      const specifier = "pdf-parse";
      const mod: any = await import(specifier);
      pdfParse = (mod.default ?? mod) as (buf: Buffer) => Promise<{ text: string }>;
    } catch {
      throw new Error(
        `LocalFileSource found a .pdf file at "${file}" but "pdf-parse" is not installed. ` +
          `Install it (npm install pdf-parse) or exclude .pdf from LocalFileSourceOptions.extensions.`,
      );
    }
    const buf = await readFile(file);
    const { text } = await pdfParse(buf);
    return text;
  }

  private *chunkParagraphs(text: string): Generator<string> {
    const paragraphs = text
      .split(/\n\s*\n/)
      .map((p) => p.trim())
      .filter((p) => p.length > 0);

    let buffer = "";
    for (const para of paragraphs) {
      const candidate = buffer ? `${buffer}\n\n${para}` : para;
      if (candidate.length > this.opts.maxChunkChars && buffer.length >= this.opts.minChunkChars) {
        yield buffer;
        buffer = para;
      } else {
        buffer = candidate;
      }
    }
    if (buffer.length >= this.opts.minChunkChars) yield buffer;
  }
}
