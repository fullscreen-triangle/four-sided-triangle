# @four-sided-triangle/individuate

A TypeScript implementation of [Federated Retrieval-Augmentation](../publications/federated-retrieval-augmentation/federated-retrieval-augmentation.tex):
retrieval as individuation against a persistent receiver graph, rather than a
top-k content-similarity lookup.

## The problem this solves

A retrieval system that returns the passage whose tokens best match your
query can be completely true and still useless: it answers "what text
overlaps my query" when what you needed was "what does this mean, to me,
given everything I already know about my own project." These are different
questions with different answers (see the paper's Thm 3.4). This package
never hands back a bare passage. `ask()` always returns a `status` that is
honest about how well-grounded the answer is, computed against a receiver
graph that accretes your own prior context rather than a global relevance
score.

## Install

```bash
npm install @four-sided-triangle/individuate
# only if you point a LocalFileSource at .pdf files:
npm install pdf-parse
```

Zero required runtime dependencies otherwise. No backend process, no Python.

## Usage

```ts
import { createIndividuator, LocalFileSource, JsonFilePersistAdapter } from "@four-sided-triangle/individuate";

const assistant = createIndividuator({
  receiverId: "kundai:my-project",
  sources: [
    new LocalFileSource({ root: "./docs", extensions: [".md", ".txt", ".pdf"] }),
  ],
  persist: new JsonFilePersistAdapter("./.individuate/receiver.json"),
});

const answer = await assistant.ask("why did the assay fail under buffer condition X");

switch (answer.status) {
  case "grounded":
    console.log(answer.claim); // backed by a coherence triangle of >=3 independent sources
    break;
  case "single-sourced":
  case "two-sourced":
    console.log(answer.claim, "—", answer.warning); // provisional, says why
    break;
  case "contested":
    console.log("sources disagree:", answer.classes); // never silently picks one
    break;
  case "declined":
    console.log(answer.reason); // nothing matched — says so, doesn't fabricate
    break;
}
```

## What each status means

| status | meaning |
|---|---|
| `grounded` | A strongly-connected triangle of ≥3 independent, mutually-supporting sources backs this claim (paper Thm 6.4). |
| `two-sourced` / `single-sourced` | Fewer than 3 independent sources agreed — reported honestly as provisional, never silently promoted. |
| `contested` | Independent sources disagree; the distinct positions are returned instead of one being picked (Thm 6.6–6.7). |
| `declined` | Nothing in the federated sources matched — the system says so rather than fabricating an answer. |

## Bringing your own sources

Implement `SourceAdapter`:

```ts
interface SourceAdapter {
  name: string;
  list(): Promise<Array<{ id: string; text: string; origin: string }>>;
}
```

Wrap an API, a database, or an existing index this way and federate it
alongside `LocalFileSource` — federation treats every source as
computationally uniform (paper Remark 2.2), with no boundary between local,
remote, and learned.

## Generative individuation and cross-source verification

Two optional capabilities need an `LLMClient` (`{ complete(args): Promise<string> }`,
bring your own adapter for any provider):

- `causalPropagationTable` — multi-hop reasoning across the graph, unified
  with static lookup as one function (paper §5).
- `routeAudit` — the four-column relaxation that catches two sources
  agreeing on surface text while silently meaning different things
  (paper §7).

## Package layout

Each module implements one part of the paper directly:

| Module | Paper section |
|---|---|
| `graph.ts` | §2 — contact graphs, resolution floor |
| `receiver.ts` | §4 — per-user accreting receiver graph, monotone history |
| `decoder.ts` | §4.2 — recognition/search identity |
| `table.ts` | §5 — causal propagation table |
| `catalysis.ts` | §6 — catalytic composition, coherence triangle |
| `closure.ts` | §6.4 — closure as the stopping rule |
| `routeAudit.ts` | §7 — four-column cross-source verification |
| `federation.ts` | §8.1 — union of federated sources |
| `waterfill.ts` / `agent.ts` / `society.ts` | §8.2–8.3 — attention allocation |

## Testing

```bash
npm test
```

The suite ports the paper's own validation experiments (§9) as fixtures —
exact floor checks, the content/meaning rank-flip instance, the coherence
triangle's robustness transition at exactly n=3, water-filling verified
against an independent grid search, and the four-column false-friend
construction. This is a correctness check against the source theorems, not
just a build check.

## Manual smoke test

```bash
npm run build
node examples/folder-query.mjs <folder> "<query>"
```
