import { buildServer } from './index.js';

const PORT = Number(process.env.PORT ?? 4000);
const HOST = process.env.HOST ?? '0.0.0.0';
const DB_PATH = process.env.DB_PATH ?? './data/four-corners.sqlite';

async function main() {
  const jwtSecret = process.env.JWT_SECRET;
  if (!jwtSecret) {
    throw new Error('JWT_SECRET environment variable is required — refusing to start with a default secret');
  }
  const app = await buildServer(jwtSecret, DB_PATH);
  await app.listen({ port: PORT, host: HOST });
}

main().catch((error: unknown) => {
  console.error('four-corners server failed to start:', error);
  process.exit(1);
});
